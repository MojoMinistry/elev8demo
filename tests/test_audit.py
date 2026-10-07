import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.robotparser import RobotFileParser

from audit import Crawler, analyze, extract, group_findings, normalize, public_host, write_report


def page(body='<title>Admissions</title><h1>Start here</h1>', url='https://example.org/admissions/'):
    return {'url': url, 'requested_url': url, 'status': 200, 'headers': {'content-type': 'text/html'}, **extract(body, url)}


class EvidenceTests(unittest.TestCase):
    def test_parse_nested_graph_and_ignore_script_as_visible_text(self):
        p = page('<title>Care &amp; Support</title><main><h1>Our <span>Care</span></h1>Welcome</main><script type="application/ld+json">{"@graph":[{"@type":["MedicalClinic","Organization"]}]}</script>')
        self.assertEqual(p['titles'], ['Care & Support'])
        self.assertEqual(p['h1'], ['Our Care'])
        self.assertNotIn('@graph', p['text'])
        self.assertEqual(p['jsonld_types'], ['MedicalClinic', 'Organization'])

    def test_malformed_json_is_evidence_not_parser_crash(self):
        p = page('<script type="application/ld+json">{bad}</script>')
        self.assertIn('invalid_jsonld', {f['code'] for f in analyze({'pages': [p]})})

    def test_header_noindex_cannot_be_missed(self):
        p = page(); p['headers']['x-robots-tag'] = 'noindex, nofollow'
        self.assertIn('noindex', {f['code'] for f in analyze({'pages': [p]})})

    def test_header_none_means_noindex(self):
        p = page(); p['headers']['x-robots-tag'] = 'none'
        self.assertIn('noindex', {f['code'] for f in analyze({'pages': [p]})})

    def test_googlebot_meta_noindex_is_retained(self):
        p = page('<meta name="googlebot" content="noindex"><title>Care</title>')
        self.assertIn('noindex', {f['code'] for f in analyze({'pages': [p]})})

    def test_fetch_failure_never_becomes_missing_seo_elements(self):
        findings = analyze({'pages': [{'url': 'https://example.org/', 'error': 'timeout'}]})
        self.assertEqual([f['code'] for f in findings], ['fetch_uncertain'])

    def test_relative_canonical_and_base(self):
        p = page('<base href="https://example.org/"><link rel="canonical" href="admissions/">')
        self.assertNotIn('nonself_canonical', {f['code'] for f in analyze({'pages': [p]})})

    def test_required_fields_scope_and_template_deduplication(self):
        html = '<form><input type="tel" required><input type="email" required><input name="honeypot"></form>'
        pages = [page(html, 'https://example.org/admissions/'), page(html, 'https://example.org/insurance/')]
        candidates = [f for f in analyze({'pages': pages}) if f['code'] == 'callback_requires_email_and_phone']
        self.assertEqual(len(candidates), 2)
        self.assertEqual(len(group_findings(candidates)), 1)
        self.assertNotIn('callback_requires_email_and_phone', {f['code'] for f in analyze({'pages': [page(html.replace('type="email" required', 'type="email"'))]})})
        separate_forms = '<form><input type="tel" required></form><form><input type="email" required></form>'
        self.assertNotIn('callback_requires_email_and_phone', {f['code'] for f in analyze({'pages': [page(separate_forms)]})})

    def test_failed_html_response_is_not_a_valid_landing_page(self):
        p = page(); p['status'] = 404
        self.assertEqual([f['code'] for f in analyze({'pages': [p]})], ['http_error'])

    def test_duplicate_titles_do_not_double_count_redirect_to_same_page(self):
        p = page()
        self.assertNotIn('duplicate_title', {f['code'] for f in analyze({'pages': [p, p]})})

    def test_query_asset_phone_and_credentials_are_excluded(self):
        for url in ['https://example.org/?action=delete', 'https://example.org/a.pdf', 'tel:5551234567', 'https://name:pass@example.org/']:
            self.assertIsNone(normalize(url))
        self.assertEqual(normalize('/care#cost', 'https://example.org/'), 'https://example.org/care')

    def test_private_literal_is_rejected_even_with_proxy(self):
        for url in ['http://127.0.0.1/', 'http://169.254.169.254/', 'http://localhost/']:
            with self.assertRaises(ValueError): public_host(url)

    def test_robots_block_issues_no_request(self):
        with tempfile.TemporaryDirectory() as folder:
            c = Crawler('https://example.org/', Path(folder))
            c.robot = RobotFileParser(); c.robot.parse(['User-agent: *', 'Disallow: /private/'])
            with patch.object(c.opener, 'open') as opener:
                result = c.fetch('https://example.org/private/')
                self.assertEqual(result['error'], 'robots_disallowed'); opener.assert_not_called()

    def test_redirect_cannot_escape_origin(self):
        with tempfile.TemporaryDirectory() as folder:
            c = Crawler('https://example.org/', Path(folder), delay=0)
            redir = HTTPError('https://example.org/', 302, 'Found', {'Location': 'https://other.example/'}, io.BytesIO(b''))
            with patch('audit.public_host'), patch.object(c.opener, 'open', side_effect=redir) as opener:
                result = c.fetch('https://example.org/')
            self.assertEqual(result['error'], 'cross_origin_redirect_excluded')
            self.assertEqual(opener.call_count, 1)

    def test_redirect_target_is_rechecked_against_robots(self):
        with tempfile.TemporaryDirectory() as folder:
            c = Crawler('https://example.org/', Path(folder), delay=0)
            c.robot = RobotFileParser(); c.robot.parse(['User-agent: *', 'Disallow: /private/'])
            redir = HTTPError('https://example.org/', 302, 'Found', {'Location': '/private/'}, io.BytesIO(b''))
            with patch('audit.public_host'), patch.object(c.opener, 'open', side_effect=redir) as opener:
                result = c.fetch('https://example.org/')
            self.assertEqual(result['error'], 'robots_disallowed')
            self.assertEqual(opener.call_count, 1)

    def test_offline_report_escapes_untrusted_page_data(self):
        data = {'target': 'https://example.org/', 'started_at': 'test', 'pages': [page('<title>&lt;script&gt;alert(1)&lt;/script&gt;</title>')]}
        with tempfile.TemporaryDirectory() as folder:
            with patch('audit.Crawler.fetch', side_effect=AssertionError('network used')):
                write_report(data, Path(folder))
            self.assertTrue((Path(folder) / 'candidate_groups.json').exists())
            self.assertNotIn('<script>alert(1)</script>', (Path(folder) / 'report.html').read_text())


if __name__ == '__main__':
    unittest.main()
