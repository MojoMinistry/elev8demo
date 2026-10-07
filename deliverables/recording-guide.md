# Five-minute screen recording

The assessment asks for **your** explanation. Record this walkthrough in your own voice after reviewing the findings. This repository contains a script, commands and a real saved run; it does not contain a claimed applicant recording.

## Prepare

Open a terminal in the cloned repository, the README, `deliverables/elev8-one-page-memo.pdf`, `evidence/findings.md`, and `sample/report.md`. Enlarge the terminal text. Use Loom or your usual screen recorder. Hide unrelated tabs/notifications.

The recorded complete crawl took about four minutes. For a reliable five-minute explanation, run a smaller **live six-page demonstration** and clearly label the submitted **38-page snapshot** when switching to it. Fresh website results can change; describe what your run actually shows.

```bash
python3 audit.py https://www.lacatc.com/ --max-pages 6 --out runs/recording
```

If network access is unavailable, demonstrate replay and explicitly call it offline:

```bash
python3 audit.py --replay sample/observations.json --out runs/recording
```

## Timed walkthrough

| Time | Screen | Suggested explanation |
| --- | --- | --- |
| 0:00-0:25 | README and live command | “I used OpenAI Codex in ChatGPT Work Mode to build this with Python's standard library. LACATC is the public treatment-center site. This demo uses six pages; the submitted evidence covers 38.” |
| 0:25-1:00 | Live output / `audit.py` | “The workflow reads robots and sitemaps, prioritizes patient decision pages, stays on one origin, and only makes GET requests. It saves the status, directives, call links, form requirements, schema, timestamp and response hash. No forms or calls are submitted.” |
| 1:00-1:30 | Generated report and `sample/report.md` | “The full run returned 200 on all 38 pages, with self-canonicals and call links. The 34 callback flags are one shared template opportunity. I combined machine checks with reviewed patient-journey evidence.” |
| 1:30-2:15 | Memo, priorities 1-2 | Explain the qualified coverage introduction versus broader metadata/card wording. Then explain the phone-plus-email callback requirement. “I'd test optional email and judge qualified admissions, contactability and spam along with completion.” |
| 2:15-3:05 | Memo, priorities 3 and 5 | Show the About page's licensing-verification step and the missing minimum age on the three reviewed pages. “These are website proof and eligibility gaps. The evidence says nothing about whether the provider actually lacks credentials. I'd validate age-related demand before expanding that work.” |
| 3:05-3:45 | E4 and AI-search-probe | Explain the conflicting detox FAQ answers retrieved by search. “I can show the source inconsistency. I haven't measured consumer ChatGPT, AI Overview or Perplexity answer share. The next step is a repeatable prompt/citation baseline after clinical review.” |
| 3:45-4:20 | Rejected diagnoses and tests | Show the raw/rendered phone-pattern distinction and mention the proxy-DNS failure. “Running the code and checking the rendered page changed the diagnosis. Tests cover redirects, robots, indexing directives, extraction and duplicate grouping.” |
| 4:20-5:00 | Short answers and measurement | “I'd first get query/page/device exposure from GSC and answered, qualified calls through admissions from tracking/CRM. Clicks are proxies. Another ten hours would add those outcomes, mobile rendering checks, provider-fact validation and a small AI-answer baseline.” |

Commands you can show without contacting the facility:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/verify_evidence.py runs/lacatc/observations.json
```

The second command requires the full live crawl, not the compact published snapshot. If you use replay, show the checked-in evidence instead.

## Before sending

- Confirm you have no connection to the selected facility.
- Review the five judgments, especially the lower-confidence age/AI impact assumptions.
- Record the screen and your explanation, then copy your real video link into the application email.
- Send the repository link, one-page memo, two short answers and video link within the requested three-business-day window. The receipt date was not supplied here, so a deadline was not invented.
