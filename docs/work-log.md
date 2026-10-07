# Work log and AI disclosure

**Tool:** OpenAI Codex in ChatGPT Work Mode, using shell/Python, public web search and read-only browser inspection. No paid SEO API or runtime LLM integration. The AI wrote the code and draft analysis, then revised them against executed checks. The applicant should review and explain the work before submitting.

**Timebox:** session began around 2026-10-07 13:10 UTC (06:10 Pacific). Local package validation completed at 2026-10-07 13:49 UTC. About 39 elapsed minutes to this checkpoint, including a slow initial browser startup. The personal recording and application submission remain outside this completed work.

## Actual work

1. Confirmed the supplied public GitHub repository was empty and cloned it.
2. Selected LACATC from public U.S. treatment-center search results. No prior relationship was known from the available context; the applicant must personally confirm independence.
3. Built the standard-library crawler and ran it on the public site. The first run exposed an environment/proxy DNS mismatch; the public-host check was corrected.
4. Full crawl began 2026-10-07T13:16:20.241633+00:00 and ended 2026-10-07T13:20:27.698471+00:00: 38 pages, 40 HTTP requests including robots and sitemap. All pages returned HTTP 200. Full snapshots stayed local; a compact technical extract was published.
5. Inspected source text and JSON-LD, then checked rendered Admissions and About pages. No fields were filled, forms submitted, calls placed, or chats sent.
6. Queried public search for pain-related detox answers and recorded the contrasting source snippets. Consumer AI product responses were not captured.
7. Grouped the repeated callback flags, rejected unsupported diagnoses, wrote five ranked findings with a measurement plan, short answers, a recording guide and twelve ARC42 sections.
8. Ran the tests, exact evidence checks and offline replay. Generated and visually reviewed the one-page PDF.

## Verification commands executed

```bash
python audit.py https://www.lacatc.com/ --max-pages 45 --out runs/lacatc
python -m unittest discover -s tests -v
python scripts/publish_snapshot.py runs/lacatc/observations.json --out sample
python scripts/verify_evidence.py runs/lacatc/observations.json
python audit.py --replay sample/observations.json --out runs/replay
cmp sample/candidates.json runs/replay/candidates.json
cmp sample/candidate_groups.json runs/replay/candidate_groups.json
```

Results: **16 tests passed; 10 evidence checks passed; replay candidate files matched.** PDF checked as one page, six link annotations, then rendered with Poppler and visually inspected. The optional PDF renderer used the installed ReportLab runtime and embeds fonts.

## Deliberate limits

The work establishes public observations, not lost admissions or current clinical/insurance facts. Four of the final five findings require editorial judgment; the automatic scan supplied the callback flag plus a baseline inventory. There is no fabricated consumer-AI response, patient conversion data, applicant screen recording, or claim that the facility lacks credentials. Actual impact needs authorized aggregate GSC/call/CRM evidence.

## Additional Clearview run

Pulled main at bfa9666 and followed README on Clearview. Live bounded crawl, source inspection, rendered desktop review of program/admissions, public retrieval of family FAQ, sanitized technical export and five review priorities are documented in ../audits/clearview/findings.md. Test suite: 16 passed. No changes to crawler code. Original LACATC submission remains the primary assessment.
