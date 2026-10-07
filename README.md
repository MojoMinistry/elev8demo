# elev8 | Patient-inquiry SEO audit

A small, reusable public-site audit built with **OpenAI Codex in ChatGPT Work Mode** for the Product Performance Lead exercise. Runtime: **Python 3.10+**, standard library only, no API key or paid SEO service.

**Assessment site:** [Los Angeles County Addiction Treatment Center (LACATC)](https://www.lacatc.com/), Encino, California. Public observations collected October 7, 2026. The applicant should confirm the exercise's no-connection requirement before submission.

## Start here

- [One-page memo (PDF)](deliverables/elev8-one-page-memo.pdf) / [editable text](deliverables/memo.md)
- [Five findings and evidence](evidence/findings.md)
- [Two short answers](deliverables/short-answers.md)
- [Five-minute recording guide](deliverables/recording-guide.md)
- [ARC42 architecture](docs/arc42.md)
- [Saved crawl inventory](sample/report.md) / [technical evidence](sample/observations.json)

## Run on a website

```bash
git clone https://github.com/MojoMinistry/elev8demo.git
cd elev8demo
python3 audit.py https://www.lacatc.com/ --max-pages 45 --out runs/lacatc
```

Use `python` if that is your Python 3 command. Open `runs/lacatc/report.html` in a browser, then review `candidate_groups.json`. Change the URL and output folder to audit another facility. Use the site's final HTTPS hostname: cross-origin redirects intentionally stop.

The recorded run took about four minutes: **38 pages + robots.txt + sitemap = 40 HTTP requests**. All 38 pages returned 200, had one H1, self-canonicals, call links, and parseable JSON-LD. The automated rules identified one shared callback-form opportunity on 34 intent-matched pages. Four additional editorial findings came from source and browser review. The five priorities are documented judgments, not five independently detected technical failures.

## Replay without waiting or making requests

```bash
python3 audit.py --replay sample/observations.json --out runs/replay
python3 -m unittest discover -s tests -v
```

Replay reruns the technical rules on the October 7 snapshot. The published snapshot contains technical facts; full third-party page text and HTML stay in local, gitignored `runs/`. Replay does not revalidate current website content or editorial conclusions.

To verify the memo's evidence after a fresh crawl:

```bash
python3 scripts/verify_evidence.py runs/lacatc/observations.json
```

This checks exact evidence strings and selected fields. An absence check is a review aid; inspect the full page before reaching a conclusion.

## Repeatable workflow

1. **Collect:** read robots.txt, discover sitemap URLs and internal links, prioritize admissions/insurance/program pages, make bounded same-origin GET requests.
2. **Detect:** inventory HTTP status, directives, canonicals, titles, H1s, call links, form requirements and JSON-LD. Save timestamps, selected headers, hashes, redirect chains and local HTML.
3. **Validate:** group shared-template issues; open affected pages; compare source to rendered behavior. Treat fetch failures as uncertainty. Use the [manual review checklist](docs/review-checklist.md) for payer facts, provider identity, patient eligibility and answer consistency.
4. **Prioritize:** use proximity to a patient decision, number of affected entry points, confidence and effort. Separate observed facts from expected effects on qualified calls and admissions. Do not invent traffic or revenue estimates.
5. **Explain:** publish five evidence-backed findings, the fix, the first GSC/call-data check and the remaining uncertainty. Record the actual run and the decisions in your own voice.

## Ground rules and limits

GET-only; no submitted forms, phone calls, chats or facility contact. Robots-aware, sequential requests with at least a one-second default gap, 45-page demo budget, 3 MB response cap and 20-second request timeout. Query URLs and common downloadable assets are excluded. The audit requests no authenticated/private data.

This is a timeboxed diagnostic. It does not measure rank, impressions, Core Web Vitals, actual call completion, form delivery, admission conversion, complete Google indexing, or consumer AI citation share. Raw HTML extraction does not prove rendered visibility. JSON-LD presence is not a rich-result guarantee; absence is not an AI exclusion. Search snippets are retrieval evidence, not observed Google AI Overview or Perplexity answers. See [limitations](docs/arc42.md#11-risks-and-technical-debt).

The applicant's personal five-minute screen recording is the remaining submission item. A timed script and live/replay commands are included; an applicant recording has not been fabricated.

## Optional memo rebuild

The crawler has no dependencies. Rebuilding the PDF requires ReportLab:

```bash
python3 -m pip install reportlab
python3 scripts/build_memo.py
```

The checked-in PDF is ready to read. [Work log and AI disclosure](docs/work-log.md) identify what was actually run and reviewed.
