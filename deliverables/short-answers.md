# Two short answers

## Where was the AI wrong or unreliable, and how was it caught?

The first Codex-generated crawler assumed local DNS resolution was available. Its live run failed before fetching the site, while an independent HTTP request succeeded through the environment's managed proxy. The check was corrected to support proxy-resolved public domains while retaining local/private-address rejection.

Source-only interpretation also needed checking. Extra escaping in the raw phone-input pattern suggested a possible validation defect. A read-only browser inspection showed normalized escaping after rendering, so that diagnosis was withheld. The initial scan produced 34 instances of the same callback requirement; grouping them revealed one shared-template opportunity.

Evidence checks, rendered DOM inspection and 16 targeted automated tests provided separate checks on the generated code and claims. Expected conversion effects remain hypotheses. Search retrieval exposed contradictory detox answers, but it did not establish an actual consumer-AI error or citation share.

## What would you improve with another 10 hours?

| Hours | Work | Outcome |
| --- | --- | --- |
| 0-2 | With authorized access, review 90-day GSC cohorts and aggregate call/CRM outcomes | Re-rank issues by qualified inquiries and admissions; distinguish payer/age mismatch from demand |
| 2-4 | Add bounded browser checks, mobile screenshots, accessibility/CTA checks and PageSpeed/CrUX evidence where available | Separate source/render differences and real user performance; test forms on a staging site with explicit permission |
| 4-6 | Validate provider identity, public licensing records, clinical ownership and payer wording | Publishable factual corrections approved by appropriate facility owners |
| 6-8 | Run and archive repeated consumer-AI prompts across products/locales | A small baseline of answer accuracy, citations and source consistency |
| 8-10 | Harden robots handling, sitemap/redirect coverage and report diffs; design one callback experiment | More reliable reuse plus a measurable first intervention |

If private access is unavailable, spend the first two hours on public demand/competitor sampling and clearly keep conversion attribution open. I would prioritize one instrumented callback change and the coverage corrections before expanding the crawler into a larger platform.
