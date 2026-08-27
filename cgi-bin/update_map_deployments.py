#!/usr/bin/env python3
"""
update_map_deployments.py

Reads ~/processing/deployments/active_deployments.txt and writes
~/public_html/mapserver/deployments.json with full HTTPS URLs for
each active deployment KML.

Run manually or from cron, e.g.:
  */15 * * * * /usr/bin/python3 ~/processing/deployments/update_map_deployments.py
"""

import json
from pathlib import Path

BASE_URL = 'https://cproof.uvic.ca/gliderdata/deployments'

COLORS = [
    '#e74c3c',  # red
    '#3498db',  # blue
    '#2ecc71',  # green
    '#f39c12',  # orange
    '#9b59b6',  # purple
    '#1abc9c',  # teal
    '#e67e22',  # dark orange
    '#e91e63',  # pink
    '#00bcd4',  # cyan
    '#8bc34a',  # lime
]

home        = Path.home()
active_file = home / 'processing' / 'deployments' / 'active_deployments.txt'
out_file    = home / 'public_html' / 'mapserver' / 'deployments.json'

if not active_file.exists():
    print(f'No active deployments file at {active_file}')
    out_file.write_text('[]')
    raise SystemExit(0)

lines = [l.strip() for l in active_file.read_text().splitlines() if l.strip()]

layers = []
for i, line in enumerate(lines):
    parts = line.split('/')
    if len(parts) != 2:
        print(f'Skipping unrecognised line: {line!r}')
        continue
    glider, deployment = parts
    date_str = deployment[-8:]
    label = f'{glider}  {date_str[:4]}-{date_str[4:6]}-{date_str[6:]}'
    url = f'{BASE_URL}/{glider}/{deployment}/{deployment}.kml'
    layers.append({'name': label, 'kml': url, 'color': COLORS[i % len(COLORS)]})
    print(f'  + {label}  →  {url}')

out_file.write_text(json.dumps(layers, indent=2))
print(f'Wrote {out_file}  ({len(layers)} deployments)')
