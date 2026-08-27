#!/usr/bin/env python3
"""
logs_api.py — CGI backend for the C-PROOF pilot operations log (ops_log.html).

Stdlib only, no third-party dependencies. Deployed as a plain CGI script
alongside mapserv (see mapserver.conf for the pattern this follows).

Data layout on disk, per mission:

    <BASE>/<glider>/<mission>/pilot_log/log.txt              (append-only entries)
    <BASE>/<glider>/<mission>/pilot_log/status.txt           (current status/plan, whole-file)
    <BASE>/<glider>/<mission>/pilot_log/status_archive/      (superseded status.txt snapshots)
    <BASE>/<glider>/<mission>/pilot_log/.lock                (advisory lock, both files)

(named pilot_log/, not logs/, since logs/ is already used for glider-generated
files in the deployment directory)

<BASE> defaults to ~/processing/deployments (same directory active_deployments.txt
already lives in), or can be overridden with the OPS_LOG_BASE environment
variable — set that for local testing so you don't touch real deployment data.

Log entry format (log.txt), oldest entry first, human-readable:

    ##### 2026-08-22T21:32:00Z | Jody
    Deployed at station P4, heading northwest per plan.

    ##### 2026-08-22T18:05:00Z | Jody
    Diverted around fishing gear near waypoint 3.

status.txt has no header — it is exactly the plan text a pilot typed in,
nothing else, so it stays plain and readable if opened directly.

Before each save overwrites status.txt, the previous contents are copied into
status_archive/ under a name carrying the old file's mtime, e.g.
status_archive/status_2026-08-23T14-05-00Z.txt. A save that doesn't actually
change the text (double-click Save with no edits) does not create a new
archive entry.

API (query string action=..., JSON body for POST):

    GET  ?action=list_active
    GET  ?action=list_archive
    GET  ?action=get_mission&glider=G&mission=M
    GET  ?action=export_all
    POST ?action=add_entry     {glider, mission, pilot, text}
    POST ?action=save_status   {glider, mission, text, base_mtime, pilot}

All responses are JSON, except export_all, which returns a single
text/plain download: every mission's status/plan plus full log,
concatenated, grouped by glider then mission (mission names sort
chronologically already, e.g. dfo-hal1002-20240513). Meant for the rare
"search everything" case — small enough to just grep or hand to an AI
rather than needing a real search backend. Errors use a non-200 CGI
Status header and a JSON body of the form {"error": "message"}.

Slack (optional): if a per-glider incoming webhook URL is configured (see
SLACK_CONFIG_PATH below), every successful add_entry and save_status also
posts a message to that glider's channel. Missing config, or a Slack request
that fails, never blocks or fails the actual save -- it's fire-and-forget,
with any problem logged to stderr only.
"""

import fcntl
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ENTRY_HEADER_RE = re.compile(r'^##### (\S+) \| ?(.*)$')
SAFE_NAME_RE = re.compile(r'^[A-Za-z0-9_.-]+$')


def base_dir():
    override = os.environ.get('OPS_LOG_BASE')
    if override:
        return Path(override)
    return Path.home() / 'processing' / 'deployments'


# ── Slack (optional) ────────────────────────────────────────────────────────
# JSON file mapping glider name -> incoming webhook URL for that glider's
# channel, e.g. {"stella": "https://hooks.slack.com/services/...", ...}.
# Defaults to a file named slack_webhooks.json next to this script; override
# with OPS_LOG_SLACK_CONFIG. If the file doesn't exist, or a glider has no
# entry in it, Slack posting is silently skipped for that glider.
_slack_config_cache = None


def slack_config():
    global _slack_config_cache
    if _slack_config_cache is not None:
        return _slack_config_cache
    override = os.environ.get('OPS_LOG_SLACK_CONFIG')
    path = Path(override) if override else (Path(__file__).resolve().parent / 'slack_webhooks.json')
    try:
        _slack_config_cache = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        _slack_config_cache = {}
    return _slack_config_cache


def notify_slack(glider, text):
    url = slack_config().get(glider)
    if not url:
        return
    if len(text) > 2900:
        text = text[:2900] + '… (truncated)'
    payload = json.dumps({'text': text}).encode('utf-8')
    req = urllib.request.Request(
        url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        urllib.request.urlopen(req, timeout=5).read()
    except (urllib.error.URLError, OSError) as e:
        print(f'logs_api.py: Slack post for {glider!r} failed: {e!r}', file=sys.stderr)


class ApiError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


def require_safe_name(value, field):
    if not value or not SAFE_NAME_RE.match(value):
        raise ApiError(400, f'invalid {field!r}: {value!r}')
    return value


def mission_dir(glider, mission, create=False):
    require_safe_name(glider, 'glider')
    require_safe_name(mission, 'mission')
    d = base_dir() / glider / mission / 'pilot_log'
    if create:
        d.mkdir(parents=True, exist_ok=True)
    return d


def read_active():
    """Returns list of (glider, mission) tuples from active_deployments.txt."""
    active_file = base_dir() / 'active_deployments.txt'
    if not active_file.exists():
        return []
    out = []
    for line in active_file.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split('/')
        if len(parts) != 2:
            continue
        glider, mission = parts
        if SAFE_NAME_RE.match(glider) and SAFE_NAME_RE.match(mission):
            out.append((glider, mission))
    return out


def locked(mdir):
    """Context manager: advisory exclusive lock over a mission's log files."""
    mdir.mkdir(parents=True, exist_ok=True)
    lock_path = mdir / '.lock'
    fh = open(lock_path, 'a+')

    class _Lock:
        def __enter__(self_inner):
            fcntl.flock(fh, fcntl.LOCK_EX)
            return fh

        def __exit__(self_inner, *exc):
            fcntl.flock(fh, fcntl.LOCK_UN)
            fh.close()

    return _Lock()


def archive_status(mdir, old_text, old_mtime):
    """Snapshot the status.txt text being superseded into status_archive/,
    named by the timestamp it was last saved at. Call this while still
    holding the mission's lock, before status.txt is overwritten. A
    filename collision (two saves landing in the same second) is resolved
    by appending -1, -2, ... rather than clobbering the earlier snapshot."""
    archive_dir = mdir / 'status_archive'
    archive_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime('%Y-%m-%dT%H-%M-%SZ', time.gmtime(old_mtime))
    dest = archive_dir / f'status_{ts}.txt'
    suffix = 1
    while dest.exists():
        dest = archive_dir / f'status_{ts}-{suffix}.txt'
        suffix += 1
    dest.write_text(old_text)


def parse_entries(text):
    """Parse log.txt content into a list of {timestamp, pilot, text} dicts,
    oldest first (file order)."""
    if not text.strip():
        return []
    entries = []
    lines = text.splitlines()
    current = None
    body_lines = []

    def flush():
        if current is not None:
            body = '\n'.join(body_lines).strip('\n')
            entries.append({
                'timestamp': current[0],
                'pilot': current[1],
                'text': body,
            })

    for line in lines:
        m = ENTRY_HEADER_RE.match(line)
        if m:
            flush()
            current = (m.group(1), m.group(2))
            body_lines = []
        else:
            if current is not None:
                body_lines.append(line)
    flush()
    return entries


def action_list_active():
    active = read_active()
    return {'missions': [{'glider': g, 'mission': m} for g, m in active]}


def action_list_archive():
    active = set(read_active())
    base = base_dir()
    out = []
    if base.exists():
        for glider_dir in sorted(base.iterdir()):
            if not glider_dir.is_dir():
                continue
            glider = glider_dir.name
            if not SAFE_NAME_RE.match(glider):
                continue
            for mission_d in sorted(glider_dir.iterdir()):
                if not mission_d.is_dir():
                    continue
                mission = mission_d.name
                if not SAFE_NAME_RE.match(mission):
                    continue
                logs_d = mission_d / 'pilot_log'
                if not logs_d.is_dir():
                    continue
                if (glider, mission) in active:
                    continue
                log_file = logs_d / 'log.txt'
                status_file = logs_d / 'status.txt'
                last_updated = None
                for f in (log_file, status_file):
                    if f.exists():
                        mt = f.stat().st_mtime
                        if last_updated is None or mt > last_updated:
                            last_updated = mt
                out.append({
                    'glider': glider,
                    'mission': mission,
                    'last_updated': last_updated,
                })
    out.sort(key=lambda x: (x['last_updated'] or 0), reverse=True)
    return {'missions': out}


def action_export_all():
    """Concatenate every mission's status/plan and full log into one
    plain-text blob, grouped by glider then mission. Missions with no
    pilot_log/ content at all are skipped. Meant to be downloaded and
    grepped, or pasted into an AI chat, for the rare cross-mission
    question -- not for anything that needs to run often or fast."""
    active = set(read_active())
    base = base_dir()
    lines = [
        'C-PROOF Pilot Ops Log -- full export',
        'Generated: ' + time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        '',
    ]

    if base.exists():
        for glider_dir in sorted(base.iterdir()):
            if not glider_dir.is_dir():
                continue
            glider = glider_dir.name
            if not SAFE_NAME_RE.match(glider):
                continue
            for mission_d in sorted(glider_dir.iterdir()):
                if not mission_d.is_dir():
                    continue
                mission = mission_d.name
                if not SAFE_NAME_RE.match(mission):
                    continue
                logs_d = mission_d / 'pilot_log'
                if not logs_d.is_dir():
                    continue

                log_file = logs_d / 'log.txt'
                status_file = logs_d / 'status.txt'
                if not log_file.exists() and not status_file.exists():
                    continue

                tag = 'ACTIVE' if (glider, mission) in active else 'archived'
                lines.append('=' * 80)
                lines.append(f'{glider} / {mission}  [{tag}]')
                lines.append('=' * 80)
                lines.append('')

                status_text = status_file.read_text().strip() if status_file.exists() else ''
                lines.append('--- Status / plan ---')
                lines.append(status_text or '(none)')
                lines.append('')

                log_text = log_file.read_text().strip() if log_file.exists() else ''
                lines.append('--- Log entries (oldest first) ---')
                lines.append(log_text or '(no entries)')
                lines.append('')
                lines.append('')

    return '\n'.join(lines)


def action_get_mission(params):
    glider = require_safe_name(params.get('glider', [''])[0], 'glider')
    mission = require_safe_name(params.get('mission', [''])[0], 'mission')
    mdir = mission_dir(glider, mission, create=False)

    log_file = mdir / 'log.txt'
    status_file = mdir / 'status.txt'

    entries = []
    if log_file.exists():
        entries = parse_entries(log_file.read_text())
    entries.reverse()  # newest first for the reader pane

    status_text = ''
    status_mtime = None
    if status_file.exists():
        status_text = status_file.read_text()
        status_mtime = status_file.stat().st_mtime

    active = (glider, mission) in set(read_active())

    return {
        'glider': glider,
        'mission': mission,
        'is_active': active,
        'entries': entries,
        'status': {'text': status_text, 'mtime': status_mtime},
    }


def action_add_entry(body):
    glider = require_safe_name(body.get('glider', ''), 'glider')
    mission = require_safe_name(body.get('mission', ''), 'mission')
    pilot = (body.get('pilot') or '').strip().replace('\n', ' ')
    text = (body.get('text') or '').strip()
    if not text:
        raise ApiError(400, 'entry text is empty')

    mdir = mission_dir(glider, mission, create=True)
    log_file = mdir / 'log.txt'
    timestamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

    header = f'##### {timestamp} | {pilot}'
    block = header + '\n' + text + '\n\n'

    with locked(mdir):
        with open(log_file, 'a') as f:
            f.write(block)

    who = pilot or 'unknown'
    notify_slack(glider, f'*{who}* logged an entry for `{glider}` / `{mission}`:\n> {text}')

    return {'entry': {'timestamp': timestamp, 'pilot': pilot, 'text': text}}


def action_save_status(body):
    glider = require_safe_name(body.get('glider', ''), 'glider')
    mission = require_safe_name(body.get('mission', ''), 'mission')
    text = body.get('text', '')
    base_mtime = body.get('base_mtime')
    pilot = (body.get('pilot') or '').strip().replace('\n', ' ')

    mdir = mission_dir(glider, mission, create=True)
    status_file = mdir / 'status.txt'

    with locked(mdir):
        current_mtime = status_file.stat().st_mtime if status_file.exists() else None
        stale = False
        if current_mtime is None and base_mtime not in (None, 0):
            stale = True
        elif current_mtime is not None:
            if base_mtime is None:
                stale = True
            elif abs(float(base_mtime) - current_mtime) > 0.001:
                stale = True

        if stale:
            current_text = status_file.read_text() if status_file.exists() else ''
            raise ApiError(409, json.dumps({
                'conflict': True,
                'current': {'text': current_text, 'mtime': current_mtime},
            }))

        if status_file.exists():
            old_text = status_file.read_text()
            if old_text != text:
                archive_status(mdir, old_text, current_mtime)

        tmp = status_file.with_suffix('.txt.tmp')
        tmp.write_text(text)
        os.replace(tmp, status_file)
        new_mtime = status_file.stat().st_mtime

    who = pilot or 'unknown'
    notify_slack(glider, f':memo: *{who}* updated the status/plan for `{glider}` / `{mission}`:\n> {text}')

    return {'mtime': new_mtime}


def read_request_body():
    try:
        length = int(os.environ.get('CONTENT_LENGTH', '0') or '0')
    except ValueError:
        length = 0
    if length <= 0:
        return {}
    raw = sys.stdin.buffer.read(length)
    if not raw:
        return {}
    try:
        return json.loads(raw.decode('utf-8'))
    except json.JSONDecodeError:
        raise ApiError(400, 'malformed JSON body')


def main():
    method = os.environ.get('REQUEST_METHOD', 'GET')
    query = {}
    from urllib.parse import parse_qs
    query = parse_qs(os.environ.get('QUERY_STRING', ''))
    action = (query.get('action', [''])[0])

    try:
        if method == 'GET':
            if action == 'list_active':
                result = action_list_active()
            elif action == 'list_archive':
                result = action_list_archive()
            elif action == 'get_mission':
                result = action_get_mission(query)
            elif action == 'export_all':
                emit_text(200, action_export_all(), filename='cproof_ops_log_export.txt')
                return
            else:
                raise ApiError(404, f'unknown GET action {action!r}')
        elif method == 'POST':
            body = read_request_body()
            if action == 'add_entry':
                result = action_add_entry(body)
            elif action == 'save_status':
                result = action_save_status(body)
            else:
                raise ApiError(404, f'unknown POST action {action!r}')
        else:
            raise ApiError(405, f'unsupported method {method!r}')

        emit(200, result)

    except ApiError as e:
        # save_status packs a JSON payload as the message for 409s; pass it
        # through as-is, otherwise wrap the plain message.
        if e.status == 409:
            emit(e.status, json.loads(e.message))
        else:
            emit(e.status, {'error': e.message})
    except Exception as e:  # pragma: no cover - defensive
        print(f'logs_api.py internal error: {e!r}', file=sys.stderr)
        emit(500, {'error': 'internal server error'})


STATUS_TEXT = {
    200: 'OK', 400: 'Bad Request', 404: 'Not Found',
    405: 'Method Not Allowed', 409: 'Conflict', 500: 'Internal Server Error',
}


def emit(status, obj):
    body = json.dumps(obj).encode('utf-8')
    sys.stdout.buffer.write(f'Status: {status} {STATUS_TEXT.get(status, "")}\r\n'.encode())
    sys.stdout.buffer.write(b'Content-Type: application/json; charset=utf-8\r\n')
    sys.stdout.buffer.write(f'Content-Length: {len(body)}\r\n\r\n'.encode())
    sys.stdout.buffer.write(body)
    sys.stdout.buffer.flush()


def emit_text(status, text, filename=None):
    body = text.encode('utf-8')
    sys.stdout.buffer.write(f'Status: {status} {STATUS_TEXT.get(status, "")}\r\n'.encode())
    sys.stdout.buffer.write(b'Content-Type: text/plain; charset=utf-8\r\n')
    if filename:
        sys.stdout.buffer.write(f'Content-Disposition: attachment; filename="{filename}"\r\n'.encode())
    sys.stdout.buffer.write(f'Content-Length: {len(body)}\r\n\r\n'.encode())
    sys.stdout.buffer.write(body)
    sys.stdout.buffer.flush()


if __name__ == '__main__':
    main()
