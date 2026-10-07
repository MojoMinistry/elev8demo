#!/usr/bin/env python3
"""Export technical observations for review without republishing full site content."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit import write_report

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('observations', type=Path)
ap.add_argument('--out', type=Path, default=Path('sample'))
args = ap.parse_args()
data = deepcopy(json.loads(args.observations.read_text()))
data['publication_note'] = 'Technical extract only. Full page text, script bodies, JSON-LD content and HTML snapshots remain in gitignored local runs. The snapshot paths and hashes identify the original responses. Replay re-runs technical rules; a live crawl is required to recheck editorial findings.'
for p in data['pages']:
    p['jsonld_count'] = len(p.get('jsonld', []))
    p['description_count'] = len(p.get('descriptions', []))
    for key in ('text', 'main_text', 'jsonld', 'descriptions'):
        p.pop(key, None)
    p['links'] = [{'url': a['url'], 'rel': a['rel']} for a in p.get('links', [])]
    p['phones'] = [{'href': a['href']} for a in p.get('phones', [])]
write_report(data, args.out)
