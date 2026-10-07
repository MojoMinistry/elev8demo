# ARC42 architecture: public-site patient-inquiry audit

Version 0.1 | October 7, 2026 | AI coding tool: OpenAI Codex in ChatGPT Work Mode

## 1. Introduction and goals

Build a workflow that can inspect a different U.S. treatment-center website tomorrow, surface SEO/conversion evidence, and support five patient-inquiry priorities. The exercise is timeboxed to 90 minutes; compact, explainable evidence and honest limits matter more than a product UI.

| Stakeholder | Need |
| --- | --- |
| Applicant | Runnable code, defensible SEO judgment, short memo, recording outline |
| Evaluator | Reproducibility, evidence trail, visible AI corrections, clarity about impact |
| Analyst using the workflow next | Change the target URL, rerun, compare facts, apply judgment |
| Subject facility and prospective patients | Public-only inspection; no unsolicited contacts or invented medical/provider claims |

Quality priorities: auditability, repeatability, bounded network behavior, readable implementation and admission relevance. The code identifies candidate evidence; a reviewer owns interpretation and the final ranking.

## 2. Architecture constraints

- Python 3.10+, standard library runtime; no paid tools, credentials or LLM API required to run.
- Public HTTP(S), GET only. No submitted forms, chats, phone calls or authenticated resources.
- Exact-origin scope; redirects to another hostname or protocol are recorded and stopped. Start with the final public HTTPS URL.
- Sequential fetches; default one-second minimum interval, 20-second request timeout, 3 MB response cap, 100-page absolute page budget and eight sitemap-document budget.
- The example uses a 45-page budget and discovers 38 pages. Page budget excludes robots/sitemaps and redirect hops; these requests are individually recorded.
- A screen recording of the applicant personally explaining the work remains an applicant task. The repository supplies a five-minute guide and real saved evidence.
- Documentation and assessment outputs live in the same Git repository. Local raw website copies remain ignored.

## 3. System scope and context

| External element | Input/output | Trust boundary |
| --- | --- | --- |
| Analyst | Supplies public URL, limits and output directory; reviews evidence | Local CLI; no background scheduling |
| Public facility website | Robots, sitemaps, HTML, response metadata | Untrusted content, never executed by the crawler |
| Operating system / HTTP proxy | DNS, HTTPS and outbound HTTP | Environment transport and egress controls apply |
| Manual browser / search tools | Rendered DOM, source retrieval, policy references | Independent observations; no hidden integration with the CLI |
| Git repository / local reports | Code, compact sample, evidence cards, memo, architecture | Publication intentionally excludes full third-party page copies and patient data |

The CLI has no connection to GSC, analytics, call tracking, an admissions CRM, Google Business Profile management, or consumer AI products. Those are later evidence sources that require separate access or manual review.

## 4. Solution strategy

Use deterministic collection and checks for facts, followed by a small explicit editorial review for commercial meaning. A missed call button and an unsupported payer assertion require different kinds of evidence; the report preserves that distinction.

Record response time, status, selected headers, redirects and a content hash before interpreting a page. Distinguish network uncertainty from an HTML defect. Save raw HTML locally for later inspection. Export a compact technical snapshot so reviewers can rerun the checks without network access. Group repeated template flags before prioritization.

The five findings use qualitative ranking: patient-decision proximity, reach, observation confidence, plausible admissions mechanism and effort. No invented lost-lead/revenue model is used.

## 5. Building-block view

| Block | Responsibility | Files / interfaces |
| --- | --- | --- |
| CLI / configuration | Validate URL, page cap, timeout and interval; choose live or replay | `audit.py:main` |
| Scope / fetcher | Public-target checks, same-origin redirects, robots gate, bounded GET, snapshot/hash | `Crawler.fetch`, `public_host`, `normalize` |
| Discovery | Read robots and nested sitemap indexes; prioritize intent paths and internal links | `Crawler.run` |
| Extraction | HTMLParser-based title/H1/directives/canonical, JSON-LD, links, forms, text | `PageParser`, `extract`, `flatten_schema` |
| Rules / grouping | Technical and callback candidates; shared-template grouping | `analyze`, `group_findings` |
| Reports | JSON observations/candidates/groups, Markdown inventory, escaped static HTML | `write_report` |
| Publication | Remove full text and JSON-LD content; retain technical facts, counts and original hashes | `scripts/publish_snapshot.py` |
| Evidence review | Exact source anchors, DOM notes, ranked judgments, policy sources | `evidence/`, `scripts/verify_evidence.py` |
| Memo rendering | Turn fixed concise memo copy into a one-page PDF | `scripts/build_memo.py`, ReportLab optional |

The collector is site-independent. The `evidence/checks.json` file is deliberately site-specific assessment evidence and is not part of the crawler's generic rules.

## 6. Runtime view

### Live audit

1. Validate the public URL and request limits; create the output directory.
2. GET robots.txt. Abort on uncertain access, an HTML challenge response, or a disallow for this crawler. A 404/410 is treated as a missing robots file.
3. Read declared same-origin sitemaps, or the conventional sitemap path. Follow at most eight sitemap documents. Parse URL sets and sitemap indexes.
4. Seed the homepage and discovered URLs, prioritizing admissions, insurance, service, program and About paths. Follow discovered same-origin HTML links up to the page budget.
5. Before each redirect target, recheck origin and robots. Fetch once per queued URL, save metadata/hash/raw bytes, parse eligible HTML. Record failures as uncertainty.
6. Apply candidate rules, group by rule and write reports. Analyst reviews source and rendered evidence, then writes findings.

### Replay

Load the supplied observations JSON, apply the same generic rules and produce reports. This path issues no requests. The shipped compact snapshot preserves fields needed by those rules. It cannot restore full source text or regenerate editorial judgment.

### Failure examples

- A network timeout yields `fetch_uncertain`, not missing-title or missing-call-link findings.
- Cross-origin redirects stop with an explicit reason and retained chain.
- An unreadable/disallowed robots file stops the run with a nonzero exit status.
- Invalid JSON-LD becomes an evidence flag without stopping extraction of the rest of the page.
- An oversized response is flagged and is not parsed as a complete page.

## 7. Deployment view

One developer laptop or execution container runs the CLI. There is no server, database, cloud deployment, third-party write integration or background worker.

```text
python3 audit.py URL --out runs/example
python3 audit.py --replay sample/observations.json --out runs/replay
python3 -m unittest discover -s tests -v
```

Reports can be opened directly as local files. `report.html` has no network resources or scripts. If a user chooses to serve it locally, they should use their usual local tooling. PDFs are prebuilt; only regeneration needs the optional ReportLab dependency.

## 8. Cross-cutting concepts

**Evidence semantics.** Each page records requested/final URL, UTC fetch time, HTTP status, selected response headers, elapsed time, body size, SHA-256, redirect chain and local snapshot path. HTML text means source-extracted text; CSS may hide it and JavaScript may modify it. A source JSON-LD observation says nothing by itself about rich-result eligibility or AI citation.

**Publication.** `sample/observations.json` contains technical facts, form attributes and source-response hashes. Raw bodies, body text, meta-description text and full JSON-LD content are omitted. `evidence/checks.json` keeps only short selected literal anchors. The snapshot path in exported records refers to the original local run; raw files are intentionally not in Git. Live recrawls may have different hashes.

**Trust.** Page content is data. The crawler never executes scripts or follows instructions found in a page. Output HTML escapes observed values. Only selected response headers are retained; cookies and authentication headers are not published. There are no runtime secrets.

**Networking.** Obvious local/private literal destinations are rejected. DNS answers are checked when local resolution is available. In a managed-proxy environment, public domain resolution may happen at the proxy; its egress policy applies. This local analyst CLI is not a hardened SSRF-safe service for arbitrary untrusted users, and must not be exposed as one.

**Robots.** The standard-library `RobotFileParser` provides the initial policy check and crawl delay. Its edge-case behavior is a known limitation; complex wildcard/agent-group policies need manual inspection before relying on an audit. Search-agent access flags are estimates from this parser, not verified requests from those agents.

**Business measurement.** Rank hypotheses using decision relevance. After access, validate against aggregate answered calls, qualified inquiries, assessments and admissions. Keep GSC query data separate from individual identities. Tel clicks and page traffic are supporting metrics.

**AI use.** Codex wrote and revised code and draft analysis. Tests and direct source/rendered checks constrained claims. No LLM runs inside the shipped CLI. The analyst can use the included review prompt with another AI tool, checking each proposal against evidence.

## 9. Architecture decisions

| Decision | Reason | Trade-off / consequence |
| --- | --- | --- |
| ADR-001: standard-library CLI | Fast setup, transparent behavior and reuse inside a 90-minute assessment | Basic HTML parser and robots semantics; no rendered browser automation |
| ADR-002: exact-origin, GET-only collection | Keep interaction bounded and prevent form/call actions | www/protocol redirects require the analyst to restart at the verified final origin |
| ADR-003: evidence before inference | Avoid turning a failed fetch or schema heuristic into a business claim | Four final findings require editorial review |
| ADR-004: technical replay snapshot | Allow a reviewer to run it without network and avoid wholesale site republication | Replay proves rule repeatability, not current source content |
| ADR-005: group candidates by shared rule | Avoid presenting 34 instances of one form pattern as independent priorities | Manual review still needed where one rule covers unrelated root causes |
| ADR-006: explicit AI-answer limits | Separate retrievable source contradictions from actual consumer product responses | Additional work is needed to measure AI citations/share |
| ADR-007: defer platform features | Keep attention on qualified inquiries and evidence | No scheduling, dashboard service, database or automatic revenue model |

## 10. Quality requirements and verification

| Scenario | Expected result | Evidence |
| --- | --- | --- |
| Run from a fresh Python 3 environment | Crawl and report without installing packages | Successful 38-page real run with standard-library Python |
| Re-run saved technical evidence offline | Same page-level candidate rules and grouping | Replay verification against the shipped snapshot |
| Website redirects to another origin | Stop before contacting the new origin | Unit test checks exactly one request |
| Redirect enters a robots-disallowed path | Stop before fetching that path | Unit test checks policy on redirect destination |
| Server returns an error or noindex header | Preserve correct diagnostic category | HTTP error, header and meta-directive tests |
| JSON-LD is invalid or nested | Retain extraction and flag invalid syntax appropriately | Parser tests |
| Required fields occur on many pages | Group the same rule into one candidate class | Template grouping test and 34-to-one example |
| Page contains hostile markup strings | Output treats strings as text | Escaping test |
| Memo cites exact observed text | Recheck the cited fragment against the live dataset | Ten evidence-anchor checks |

The test suite uses controlled fixtures for failure cases. No tests submit a facility form or require external network access. PDF output is rendered and visually inspected for one-page layout.

## 11. Risks and technical debt

1. **Unknown impact:** no private impressions, connected calls, payer outcomes or admissions. Rank changes are expected after measurement.
2. **Bounded coverage:** the crawler stops at budgets, skips query URLs/assets and exact-origin redirects, and does not enumerate every possible orphan page. A discovered-URL count is not a complete site-index count.
3. **Raw versus rendered:** the crawler does not execute JavaScript or measure CSS visibility, layout shifts, mobile usability or Core Web Vitals. Admissions/About received targeted manual browser review, not a full rendered audit.
4. **Robots edge cases:** standard-library parsing does not fully implement every modern wildcard/longest-match/merged-group convention. Complex robots policies need a better-tested parser before broader production use. The selected site's rules are simple and allow all paths.
5. **No submission verification:** form delivery, validation edge cases, chat routing, call connection and admissions handling remain untested.
6. **AI exposure:** bots and search snippets provide source-eligibility evidence only. Actual consumer AI visibility and answer accuracy require repeated captured product sessions.
7. **Provider facts:** this assessment did not establish legal licensure, accreditation, payer network contracts, age policy or clinical efficacy. Website presentation findings must not be interpreted as absence of those capabilities.
8. **Heuristics:** intent matching can include blog paths and does not measure actual query demand. Duplicate-title and schema candidates can be intentional; every rule emits review candidates.
9. **Operational resilience:** no resumable crawl, conditional caching, retries/backoff or request-level global budget. DNS failures outside a proxy can abort the run; existing raw snapshots remain local. Response timing is environment-dependent and is not a performance score.
10. **Artifact changes:** live pages can change after observation. Hashes identify collected responses; a changed hash is not itself evidence that the relevant claim changed.

## 12. Glossary

| Term | Meaning here |
| --- | --- |
| Candidate | Automatically detected evidence requiring review |
| Finding | A reviewed, ranked issue with evidence, proposed action and uncertainty |
| Qualified inquiry | A connected inquiry fitting the provider's approved service/eligibility criteria |
| Admission | An actual care admission recorded by the provider, not a site event |
| Raw HTML | HTTP response before browser execution |
| Rendered DOM | Browser document after page scripts have run |
| JSON-LD | One structured-data format; its presence does not prove eligibility or visibility |
| GSC | Google Search Console |
| AI source retrieval | Search finding an answer-bearing passage that an AI workflow could use |
| AI answer share | How often a facility is actually mentioned/cited across a defined consumer prompt sample; unmeasured here |

## Additional operational evidence: Clearview

The repeat run in [audits/clearview](../audits/clearview/findings.md) exercises the existing architecture on a second origin. Crawler HTTP 403 observations require access validation; a live browser can render pages unavailable to the crawler. JavaScript-loaded callback forms, dynamic phone replacement and animated outcome values demonstrate the raw-HTML boundary and the need for rendered manual review. No architectural or runtime changes were required.
