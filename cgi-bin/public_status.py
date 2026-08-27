#!/usr/bin/env python3
"""
public_status.py — read-only, no-auth CGI endpoint for glider_status.html's
status/plan panel.

Deliberately kept separate from logs_api.py, which stays fully Basic-Auth
protected for both reads and writes. Opening this one file up to anyone
(no login) means glider_status.html can show each mission's current
status/plan text without needing credentials, while logs_api.py -- and the
ops_log.html write UI in front of it -- are untouched.

Exposes exactly one thing, deliberately: a mission's status/plan text. No
log entries, no mission listing, no full export -- the no-auth surface here
is kept as small as the actual use case.

    GET ?action=get_status&glider=G&mission=M
        -> {"text": "...", "mtime": 123456.7}   (mtime is null if unsaved)

Deploy next to logs_api.py (same cgi-bin/ directory) -- it imports shared
helpers from it, so the two files must live side by side. See
ops_log_apache.conf for the matching ScriptAlias / <Files> block.
"""

import json
import os
import sys
from pathlib import Path
from urllib.parse import parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parent))
from logs_api import ApiError, emit, mission_dir, require_safe_name  # noqa: E402


def action_get_status(params):
    glider = require_safe_name(params.get('glider', [''])[0], 'glider')
    mission = require_safe_name(params.get('mission', [''])[0], 'mission')
    mdir = mission_dir(glider, mission, create=False)
    status_file = mdir / 'status.txt'

    text = status_file.read_text() if status_file.exists() else ''
    mtime = status_file.stat().st_mtime if status_file.exists() else None
    return {'text': text, 'mtime': mtime}


def main():
    query = parse_qs(os.environ.get('QUERY_STRING', ''))
    action = query.get('action', [''])[0]

    try:
        if action == 'get_status':
            result = action_get_status(query)
        else:
            raise ApiError(404, f'unknown GET action {action!r}')
        emit(200, result)
    except ApiError as e:
        emit(e.status, {'error': e.message})
    except Exception as e:  # pragma: no cover - defensive
        print(f'public_status.py internal error: {e!r}', file=sys.stderr)
        emit(500, {'error': 'internal server error'})


if __name__ == '__main__':
    main()
