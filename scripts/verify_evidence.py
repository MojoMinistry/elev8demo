#!/usr/bin/env python3
"""Recheck the memo's literal evidence against a full live crawl, without contacting anyone."""
import argparse
import json
from pathlib import Path
import re

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('observations', type=Path)
args = ap.parse_args()
root = Path(__file__).resolve().parents[1]
data = json.loads(args.observations.read_text())
pages = {p['url']: p for p in data['pages']}
checks = json.loads((root / 'evidence/checks.json').read_text())
failures = []
for c in checks:
    p = pages.get(c['url'])
    if not p or 'text' not in p:
        failures.append(f"{c['id']}: full live observation missing"); continue
    if c['kind'] == 'contains':
        text = ' '.join(p.get(c['field'], [])) if isinstance(p.get(c['field']), list) else p.get(c['field'], '')
        if c['value'] not in text: failures.append(f"{c['id']}: evidence changed")
    elif c['kind'] == 'required_contact_fields':
        if not any({'email', 'tel'} <= {f['type'] for f in form['fields'] if f['required']} for form in p['forms']):
            failures.append(f"{c['id']}: form requirements changed")
    elif c['kind'] == 'no_age_policy_phrase':
        if re.search(c['pattern'], p['main_text'], re.I): failures.append(f"{c['id']}: possible age policy now found; review manually")
    else:
        failures.append(f"{c['id']}: unsupported check kind")
    print(f"Checked {c['id']}: {c['url']}")
if failures:
    raise SystemExit('\n'.join(failures))
print(f'{len(checks)} evidence checks passed. Semantic conclusions, rendered behavior and business impact still require review.')
