#!/usr/bin/env python3
"""Small, read-only public-site SEO audit. Python 3.10+; standard library only."""
import argparse
from collections import Counter, deque
from datetime import datetime, timezone
import hashlib
from html import escape
from html.parser import HTMLParser
import ipaddress
import json
from pathlib import Path
import re
import socket
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler, getproxies
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET

UA = 'Elev8PublicAudit/0.1 (+read-only SEO assessment)'
BOT = 'Elev8PublicAudit'
MAX_BYTES = 3_000_000
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
ASSET = re.compile(r'\.(?:pdf|jpg|jpeg|png|gif|webp|svg|mp4|mp3|zip|css|js|ico|woff2?)$', re.I)
INTENT = re.compile(r'admission|contact|insurance|program|detox|residential|outpatient|treatment|about|team', re.I)


def utc():
    return datetime.now(timezone.utc).isoformat()


def normalize(url, base=None):
    p = urlsplit(urljoin(base or url, url))
    if p.scheme not in ('http', 'https') or not p.hostname or p.username or p.password:
        return None
    # Query URLs are excluded to avoid actions, calendars, and crawl traps.
    if p.query or ASSET.search(p.path):
        return None
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path or '/', '', ''))


def origin(url):
    p = urlsplit(url)
    return p.scheme, p.hostname, p.port or (443 if p.scheme == 'https' else 80)


def public_host(url):
    """Reject local/private targets; this CLI is for public websites."""
    p = urlsplit(url)
    if p.scheme not in ('http', 'https') or p.username or p.password:
        raise ValueError('Use a public HTTP(S) URL without credentials.')
    if not p.hostname or p.hostname.lower() == 'localhost' or p.hostname.endswith(('.local', '.internal', '.localhost')):
        raise ValueError('Private/local destinations are outside the audit scope.')
    try:
        literal = ipaddress.ip_address(p.hostname)
    except ValueError:
        literal = None
    if literal and not literal.is_global:
        raise ValueError('Private/local destinations are outside the audit scope.')
    try:
        answers = socket.getaddrinfo(p.hostname, p.port or 443, type=socket.SOCK_STREAM)
    except socket.gaierror:
        # Managed HTTP proxies resolve DNS remotely. Their egress policy applies.
        if getproxies().get(p.scheme):
            return
        raise
    for answer in answers:
        if not ipaddress.ip_address(answer[4][0]).is_global:
            raise ValueError('Private/local destinations are outside the audit scope.')


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.titles, self.h1, self.description, self.canonicals, self.robots = [], [], [], [], []
        self.links, self.phones, self.forms, self.images = [], [], [], []
        self.text, self.main_text, self.scripts, self.schema, self.schema_errors = [], [], [], [], []
        self._title = self._h1 = self._script = None
        self._link = self._form = None
        self.base_href = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag not in VOID:
            self.stack.append(tag)
        if tag == 'base':
            self.base_href = a.get('href')
        if tag == 'title': self._title = []
        if tag == 'h1': self._h1 = []
        if tag == 'meta':
            name = a.get('name', '').lower()
            if name == 'description': self.description.append(a.get('content', ''))
            if name in ('robots', 'googlebot'): self.robots.append({'agent': name, 'content': a.get('content', '')})
        if tag == 'link' and 'canonical' in a.get('rel', '').lower().split():
            self.canonicals.append(a.get('href', ''))
        if tag == 'a':
            self._link = {'href': a.get('href', ''), 'text': '', 'rel': a.get('rel', '')}
        if tag == 'script':
            self._script = {'type': a.get('type', ''), 'src': a.get('src'), 'text': ''}
        if tag == 'form':
            self._form = {'action': a.get('action'), 'method': a.get('method', 'get'), 'fields': []}
        if tag in ('input', 'select', 'textarea') and self._form is not None:
            self._form['fields'].append({'tag': tag, 'name': a.get('name'), 'type': a.get('type', 'text'), 'required': 'required' in a, 'pattern': a.get('pattern'), 'label': a.get('aria-label') or a.get('placeholder')})
        if tag == 'img': self.images.append({'src': a.get('src'), 'alt_present': 'alt' in a, 'loading': a.get('loading')})

    def handle_endtag(self, tag):
        if tag == 'title' and self._title is not None:
            self.titles.append(' '.join(''.join(self._title).split())); self._title = None
        if tag == 'h1' and self._h1 is not None:
            self.h1.append(' '.join(''.join(self._h1).split())); self._h1 = None
        if tag == 'a' and self._link is not None:
            self._link['text'] = ' '.join(self._link['text'].split())
            self.links.append(self._link)
            if self._link['href'].lower().startswith('tel:'): self.phones.append(self._link)
            self._link = None
        if tag == 'form' and self._form is not None:
            self.forms.append(self._form); self._form = None
        if tag == 'script' and self._script is not None:
            s = self._script
            if s['type'].lower() == 'application/ld+json':
                try: self.schema.append(json.loads(s['text']))
                except (ValueError, TypeError) as e: self.schema_errors.append(str(e))
            if s['src']: self.scripts.append(s['src'])
            self._script = None
        if tag in self.stack:
            self.stack = self.stack[:len(self.stack) - 1 - self.stack[::-1].index(tag)]

    def handle_data(self, data):
        if self._title is not None: self._title.append(data)
        if self._h1 is not None: self._h1.append(data)
        if self._link is not None: self._link['text'] += data + ' '
        if self._script is not None: self._script['text'] += data
        if not set(self.stack).intersection({'script', 'style', 'noscript', 'head', 'template'}):
            self.text.append(data)
            if 'main' in self.stack: self.main_text.append(data)


def flatten_schema(item):
    if isinstance(item, dict):
        yield item
        for v in item.values(): yield from flatten_schema(v)
    elif isinstance(item, list):
        for v in item: yield from flatten_schema(v)


def extract(body, url):
    p = PageParser(); p.feed(body); p.close()
    text = ' '.join(' '.join(p.text).split())
    main = ' '.join(' '.join(p.main_text).split())
    types = sorted({t for node in flatten_schema(p.schema) for t in ([node['@type']] if isinstance(node.get('@type'), str) else node.get('@type', []))})
    base = urljoin(url, p.base_href) if p.base_href else url
    return {
        'titles': p.titles, 'h1': p.h1, 'descriptions': p.description,
        'canonicals': [urljoin(base, c) for c in p.canonicals], 'meta_robots': p.robots,
        'links': [{**a, 'url': urljoin(base, a['href'])} for a in p.links], 'phones': p.phones,
        'forms': p.forms, 'images_count': len(p.images),
        'images_missing_alt': sum(not i['alt_present'] for i in p.images),
        'jsonld': p.schema, 'jsonld_count': len(p.schema), 'jsonld_types': types, 'jsonld_errors': p.schema_errors,
        'script_srcs': p.scripts, 'text': text, 'main_text': main,
        'text_word_count': len(text.split()), 'main_word_count': len(main.split()),
    }


class Crawler:
    def __init__(self, start, out, delay=1.0, timeout=20):
        self.start, self.out, self.delay, self.timeout = start, out, delay, timeout
        self.root = origin(start)
        self.opener = build_opener(NoRedirect())
        self.last = 0
        self.robot = None
        self.requests = []

    def fetch(self, url, kind='page'):
        chain = []
        for _ in range(6):
            if origin(url) != self.root:
                return {'url': url, 'error': 'cross_origin_redirect_excluded', 'redirects': chain}
            if self.robot is not None and not self.robot.can_fetch(BOT, url):
                return {'url': url, 'error': 'robots_disallowed', 'redirects': chain}
            public_host(url)
            time.sleep(max(0, self.delay - (time.monotonic() - self.last)))
            started = time.monotonic(); stamp = utc()
            try:
                response = self.opener.open(Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,application/xml,text/plain;q=0.9', 'Accept-Encoding': 'identity'}), timeout=self.timeout)
            except HTTPError as e:
                response = e
            except (URLError, TimeoutError, OSError) as e:
                self.last = time.monotonic()
                row = {'url': url, 'kind': kind, 'fetched_at': stamp, 'error': str(e), 'redirects': chain}
                self.requests.append(row); return row
            with response:
                status = response.code
                headers = {k.lower(): v for k, v in response.headers.items() if k.lower() in ('content-type', 'location', 'x-robots-tag', 'date', 'last-modified', 'content-length')}
                data = response.read(MAX_BYTES + 1)
            self.last = time.monotonic()
            row = {'url': url, 'kind': kind, 'status': status, 'headers': headers, 'fetched_at': stamp, 'elapsed_ms': round((self.last - started) * 1000), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'redirects': list(chain)}
            self.requests.append({**row})
            if status in (301, 302, 303, 307, 308) and headers.get('location'):
                chain.append({'url': url, 'status': status, 'location': headers['location']})
                url = urljoin(url, headers['location']); continue
            if len(data) > MAX_BYTES:
                row['error'] = 'response_size_limit'; return row
            key = hashlib.sha256(url.encode()).hexdigest()[:16]
            ext = 'html' if kind == 'page' else 'txt'
            target = self.out / 'raw' / f'{key}.{ext}'
            target.write_bytes(data)
            row['snapshot'] = str(target.relative_to(self.out))
            charset = re.search(r'charset=([\w-]+)', headers.get('content-type', ''), re.I)
            encoding = charset.group(1) if charset else 'utf-8'
            try: row['body'] = data.decode(encoding, errors='replace')
            except LookupError: row['body'] = data.decode('utf-8', errors='replace')
            return row
        return {'url': url, 'error': 'redirect_limit', 'redirects': chain}

    def run(self, max_pages):
        self.out.mkdir(parents=True, exist_ok=True); (self.out / 'raw').mkdir(exist_ok=True)
        base = urlunsplit((*urlsplit(self.start)[:2], '/', '', ''))
        robots = self.fetch(urljoin(base, 'robots.txt'), 'robots')
        status = robots.get('status', 0)
        # Fail closed on uncertainty; a missing robots.txt (404/410) allows crawling.
        if status not in (200, 404, 410) or robots.get('error') or (status == 200 and '<html' in robots.get('body', '').lower()):
            raise ValueError('robots.txt could not be reliably read. Audit stopped; inspect the response.')
        rp = RobotFileParser(); rp.parse(robots.get('body', '').splitlines() if status == 200 else [])
        self.robot = rp
        if not rp.can_fetch(BOT, self.start): raise ValueError('robots.txt disallows this audit.')
        self.delay = max(self.delay, rp.crawl_delay(BOT) or 0)
        sm_urls = rp.site_maps() or [urljoin(base, 'sitemap.xml')]
        sm_queue, sm_seen, sitemap_pages, sitemaps = deque(sm_urls), set(), [], []
        while sm_queue and len(sm_seen) < 8:
            url = sm_queue.popleft()
            if url in sm_seen or origin(url) != self.root: continue
            sm_seen.add(url); response = self.fetch(url, 'sitemap')
            body = response.pop('body', '')
            if response.get('status') == 200:
                try:
                    xml = ET.fromstring(body)
                    locs = [e.text.strip() for e in xml.iter() if e.tag.split('}')[-1] == 'loc' and e.text]
                    if xml.tag.split('}')[-1] == 'sitemapindex': sm_queue.extend(locs)
                    elif xml.tag.split('}')[-1] == 'urlset': sitemap_pages.extend(locs)
                    else: response['parse_error'] = 'not_a_sitemap'
                except ET.ParseError: response['parse_error'] = 'invalid_xml'
            sitemaps.append(response)
        seeds = [u for u in (normalize(u) for u in sitemap_pages) if u and origin(u) == self.root]
        seeds = sorted(set(seeds), key=lambda u: (not bool(INTENT.search(urlsplit(u).path)), u))
        queue, seen, pages = deque([self.start] + seeds), set(), []
        while queue and len(pages) < max_pages:
            url = queue.popleft()
            if url in seen: continue
            seen.add(url)
            response = self.fetch(url)
            body = response.pop('body', '')
            response['requested_url'] = url
            if 'text/html' in response.get('headers', {}).get('content-type', '') and body:
                response.update(extract(body, response['url']))
                links = [normalize(a['url']) for a in response['links']]
                links = [u for u in links if u and origin(u) == self.root and u not in seen]
                queue.extend(sorted(set(links), key=lambda u: (not bool(INTENT.search(urlsplit(u).path)), u)))
            response['robots_access'] = {bot: rp.can_fetch(bot, response['url']) for bot in ('Googlebot', 'OAI-SearchBot', 'GPTBot', 'PerplexityBot')}
            pages.append(response)
            print(f"[{len(pages):02d}/{max_pages}] {response.get('status', 'ERR')} {url}", flush=True)
        return {'schema_version': 1, 'tool': UA, 'started_at': self.requests[0]['fetched_at'], 'finished_at': utc(), 'target': self.start, 'scope': {'max_pages': max_pages, 'delay_seconds': self.delay, 'mode': 'raw_html', 'forms_submitted': 0, 'pending_unique_urls': len(set(queue) - seen)}, 'robots': {k: v for k, v in robots.items() if k != 'body'}, 'sitemaps': sitemaps, 'sitemap_urls': sorted(set(sitemap_pages)), 'pages': pages, 'requests': self.requests}


def analyze(data):
    findings = []
    def add(code, page, evidence, consequence, confidence='high', weight=1):
        findings.append({'code': code, 'url': page.get('requested_url', page['url']), 'evidence': evidence, 'confidence': confidence, 'admissions_relevance': weight, 'consequence': consequence, 'status': 'candidate_for_review'})
    for p in data['pages']:
        path = urlsplit(p['url']).path
        intent = bool(INTENT.search(path)) or path == '/'
        weight = 3 if intent else 1
        if p.get('error'):
            add('fetch_uncertain', p, p['error'], 'Verify access before diagnosing a site defect.', 'low', weight); continue
        if p.get('status', 0) >= 400:
            add('http_error', p, str(p['status']), 'A broken landing page can lose inquiries.', weight=weight); continue
        directives = ' '.join(m['content'] for m in p.get('meta_robots', [])) + ' ' + p.get('headers', {}).get('x-robots-tag', '')
        if re.search(r'\b(noindex|none)\b', directives, re.I):
            add('noindex', p, directives, 'Check whether this page should be eligible for organic discovery.', weight=weight)
        if p.get('status') != 200 or 'titles' not in p: continue
        if not p['titles'] or not p['titles'][0].strip():
            add('missing_title', p, 'Empty or absent title in source', 'Searchers receive a weaker page-level relevance signal.', weight=weight)
        if len(p['canonicals']) > 1:
            add('multiple_canonicals', p, p['canonicals'], 'Resolve conflicting canonical signals.', weight=weight)
        if p['canonicals'] and normalize(p['canonicals'][0]) != normalize(p['url']):
            add('nonself_canonical', p, p['canonicals'], 'Check whether a valuable landing page is consolidated elsewhere.', 'medium', weight)
        if intent and not p['phones']:
            add('no_tel_in_source', p, 'No tel: anchor in fetched HTML', 'Review rendered mobile calling access; JS may add it.', 'medium', weight)
        if p['jsonld_errors']:
            add('invalid_jsonld', p, p['jsonld_errors'], 'Repair invalid structured data after checking rendered markup.', weight=weight)
        if not p.get('jsonld_count', len(p.get('jsonld', []))):
            add('no_jsonld_in_source', p, 'No JSON-LD in fetched HTML', 'Review entity clarity; markup absence alone proves no AI visibility loss.', 'medium', 1)
        for bot in ('Googlebot', 'OAI-SearchBot', 'PerplexityBot'):
            if not p.get('robots_access', {}).get(bot, True):
                add('search_bot_disallowed', p, bot, 'Review search crawler access; eligibility does not guarantee inclusion.', weight=weight)
        required_sets = [{f['type'] for f in form['fields'] if f['required']} for form in p['forms']]
        if intent and any({'email', 'tel'} <= types for types in required_sets):
            add('callback_requires_email_and_phone', p, 'HTML requires both email and telephone', 'Test whether collecting both reduces completed inquiries.', 'medium', weight)
    by_title = {}
    for p in data['pages']:
        title = ' '.join(p.get('titles', [])).strip().lower()
        if title and p.get('status') == 200: by_title.setdefault(title, []).append(p)
    for title, pages in by_title.items():
        if len({p['url'] for p in pages}) > 1:
            for p in pages: add('duplicate_title', p, title, 'Differentiate landing pages for patient decision intent.', 'medium', 2)
    return sorted(findings, key=lambda f: (-f['admissions_relevance'], f['code'], f['url']))


def group_findings(findings):
    """A shared template repeated across 34 URLs is one opportunity, not 34 priorities."""
    groups = {}
    for f in findings:
        g = groups.setdefault(f['code'], {'code': f['code'], 'urls': [], 'max_admissions_relevance': 0, 'status': 'candidate_for_review'})
        g['urls'].append(f['url'])
        g['max_admissions_relevance'] = max(g['max_admissions_relevance'], f['admissions_relevance'])
    return sorted(groups.values(), key=lambda g: (-g['max_admissions_relevance'], g['code']))


def write_report(data, out):
    out.mkdir(parents=True, exist_ok=True)
    findings = analyze(data)
    groups = group_findings(findings)
    (out / 'observations.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    (out / 'candidates.json').write_text(json.dumps(findings, indent=2, ensure_ascii=False) + '\n')
    (out / 'candidate_groups.json').write_text(json.dumps(groups, indent=2, ensure_ascii=False) + '\n')
    ok = sum(p.get('status') == 200 for p in data['pages'])
    counts = Counter(f['code'] for f in findings)
    lines = ['# Public-site SEO audit', '', f"Target: {data['target']}", f"Run: {data['started_at']}", f"Fetched: {len(data['pages'])} pages; HTTP 200: {ok}; candidates: {len(findings)}.", '', 'Raw HTML evidence. Candidate flags require review; counts are not estimates of lost calls.', '', '## Candidate groups', '']
    lines += [f'- {c}: {n}' for c, n in counts.items()]
    lines += ['', '## Page inventory', '', '| URL | Status | Title | JSON-LD types |', '| --- | --- | --- | --- |']
    for p in data['pages']:
        values = [p['url'], str(p.get('status', p.get('error', 'unknown'))), '; '.join(p.get('titles', [])), ', '.join(p.get('jsonld_types', []))]
        lines.append('| ' + ' | '.join(v.replace('|', '\\|').replace('\n', ' ') for v in values) + ' |')
    (out / 'report.md').write_text('\n'.join(lines) + '\n')
    rows = ''.join('<tr>' + ''.join('<td>' + escape(str(v)) + '</td>' for v in (f['code'], f['url'], f['evidence'], f['confidence'], f['consequence'])) + '</tr>' for f in findings)
    group_rows = ''.join(f"<tr><td>{escape(g['code'])}</td><td>{len(g['urls'])}</td><td>Review source and rendered behavior; validate business impact</td></tr>" for g in groups)
    page = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Elev8 public-site audit</title><style>body{{font:16px system-ui;margin:40px;max-width:1400px;color:#183046}}h1{{font-size:36px}}table{{border-collapse:collapse;width:100%;font-size:13px}}td,th{{padding:12px;text-align:left;border-bottom:1px solid #ccd7df;overflow-wrap:anywhere}}thead{{background:#edf3f5}}.stat{{display:inline-block;padding:16px;background:#edf3f5;margin:0 12px 12px 0}}p{{line-height:1.5}}summary{{cursor:pointer;padding:20px 0}}a{{color:#126579}}</style><h1>Public-site SEO audit</h1><p>{escape(data['target'])}<br>Observed {escape(data['started_at'])}</p><div class="stat">{len(data['pages'])} pages</div><div class="stat">{ok} HTTP 200</div><div class="stat">{len(groups)} candidate groups</div><p>Raw HTML observations. Verify candidates before prioritizing. Business impact and consumer AI answer share require additional evidence.</p><h2>Grouped opportunities</h2><table><thead><tr><th>Candidate</th><th>Pages</th><th>Next step</th></tr></thead><tbody>{group_rows}</tbody></table><details><summary>Inspect {len(findings)} page-level flags</summary><table><thead><tr><th>Candidate</th><th>URL</th><th>Evidence</th><th>Confidence</th><th>Why review</th></tr></thead><tbody>{rows}</tbody></table></details><p><a href="report.md">Page inventory</a> | <a href="observations.json">Technical observations</a> | <a href="candidate_groups.json">Candidate groups</a></p></html>'''
    (out / 'report.html').write_text(page)
    print(f"\nSaved {out}/report.html and evidence. {len(findings)} page flags in {len(groups)} groups; human prioritization required.")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('url', nargs='?', help='Exact public origin; start with the final HTTPS hostname')
    ap.add_argument('--out', type=Path, default=Path('runs/latest'))
    ap.add_argument('--max-pages', type=int, default=40)
    ap.add_argument('--delay', type=float, default=1.0)
    ap.add_argument('--timeout', type=float, default=20)
    ap.add_argument('--replay', type=Path, help='Re-analyze saved observations without network requests')
    args = ap.parse_args()
    if not 1 <= args.max_pages <= 100 or args.delay < 0.5 or not 1 <= args.timeout <= 60:
        ap.error('Use 1-100 pages, a delay >= 0.5 seconds, and a 1-60 second timeout.')
    if args.replay:
        data = json.loads(args.replay.read_text())
    else:
        url = normalize(args.url or '')
        if not url: ap.error('Supply a public HTTP(S) URL or --replay observations.json.')
        try: data = Crawler(url, args.out, args.delay, args.timeout).run(args.max_pages)
        except (ValueError, OSError) as e: ap.exit(2, f'Audit stopped: {e}\n')
    write_report(data, args.out)


if __name__ == '__main__':
    main()
