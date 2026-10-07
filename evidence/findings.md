# Ranked findings and evidence

Observed October 7, 2026. Technical crawl: 13:16:20-13:20:27 UTC. Exact response hashes and page timestamps are in [index.json](index.json); structured crawl observations are in [../sample/observations.json](../sample/observations.json). Full source captures stay in gitignored `runs/lacatc/raw/` and can be collected again with the README command.

Ranking uses proximity to admission, reach across high-intent entry points, confidence and likely repair effort. It is ordinal expert judgment. Traffic, lead loss, actual plan participation, clinical outcomes and admission revenue were not measured. The five findings are opportunities supported by public evidence; the business consequences remain hypotheses.

| Rank | Priority | Funnel mechanism | Reach observed | Impact confidence | Indicative implementation effort |
| --- | --- | --- | --- | --- | --- |
| 1 / E1 | Align payer claims | Better qualification and confidence before insurance verification | Medi-Cal page; related payer templates warrant review | Medium | Small content change after payer validation |
| 2 / E2 | Simplify callback requirements | More completed callback requests from organic landings | One shared pattern on 34 intent-matched pages; Admissions DOM checked | Medium | Small template experiment; measure lead quality |
| 3 / E3 | Make provider credentials verifiable | Help families complete trust checks before calling | About page and sitewide credential badges | Medium | Moderate: gather verified operator/staff records |
| 4 / E4 | Reconcile AI-retrievable detox answers | Set consistent expectations before an inquiry | Two answer-bearing pages returned by search | Low-medium | Small edit with clinical review; ongoing monitoring |
| 5 / E5 | State admission age eligibility | Improve fit for family searches and reduce unsuitable inquiries | Admissions, residential and family page main content | Medium; demand unknown | Small policy copy/link update |

## E1: Payer claims differ across surfaces

URL: <https://www.lacatc.com/insurance/medi-cal/>

The introduction explicitly makes coverage conditional on plan details, network status, authorization and clinical review. That caveat is a positive feature. The page's meta description describes multiple levels as covered, and the related detox card describes coverage without qualification. The FAQ also makes facility-level coverage assertions. This is a consistency issue across an already useful payer page; actual network participation was not adjudicated.

**Locator:** `meta[name="description"]`; first paragraph of `main`; related Medical Detox card near the bottom. Exact short evidence fragments are in [checks.json](checks.json), E1 entries. The raw `MedicalClinic.description` across the site also lists multiple payment sources without individual-plan qualifications; preserve factual, provider-approved wording there.

**Fix:** admissions/benefits staff confirm the real operator, program and payer facts, then propagate one approved coverage distinction through title/description, body, FAQ, related cards and any relevant JSON-LD. Explain verification versus coverage versus authorization clearly. Keep the existing contextual caveat.

**First data check:** 90-day GSC insurance query/page/device cohorts, then answered calls, qualified inquiries and admissions by those landing pages. Count payer/authorization disqualifications. More calls alone could be a poor result if eligibility mismatch rises. Success is an improved qualified-inquiry-to-admission rate and better-informed callers.

## E2: Callback form friction

URL: <https://www.lacatc.com/admissions/>

Both forms have required first name, last name, phone, email, relationship selection and consent. The phone/email requirement appears on 34 pages selected by the workflow's intent rule; the repeated flags represent **one template issue**. A read-only rendered DOM inspection confirmed both required attributes on Admissions and four `tel:8447141200` anchors. No fields were filled and no buttons were submitted. Whether optional email increases qualified inquiries is an experiment, not an observed conversion loss.

**Locator:** `form input[type="tel"]`, `form input[type="email"]`, their `required` attributes; `a[href^="tel:"]`. Required-field inventory is retained in the sample observations.

**Fix:** test a callback route requiring a phone number and preserving the needed consent, with email optional. Ask for extra details after the first connection when appropriate. Evaluate spam and contactability along with completion.

**First data check:** GSC device/landing-page exposure plus analytics form-start/field-error/completion events if available; call tracking/CRM for connected callbacks, qualified assessments and admissions. A button click or tel click does not establish a connected call. Count direct calls and callbacks separately before deduplicating people.

## E3: Credential proof is difficult to reach

URL: <https://www.lacatc.com/about/>

The licensing FAQ says details can be obtained on the first call. The rendered About page and raw extraction show general licensure claims and credential badges, but no facility-specific regulator record link, license identifier, or named clinical director/leadership biographies on that page. Across the crawl, the DHCS outbound link points to general Drug Medi-Cal information, rather than a facility record.

This finding concerns discoverable website proof. The review does **not** establish that the facility lacks a license, accreditation, clinicians, or qualified staff. The regulator's actual facility record was outside this timebox.

**Fix:** add the verified operator/legal identity, license identifier, program scope and authoritative verification link. Name the responsible clinical leaders with accurate credentials and link biographies from relevant programs. Get the records from the facility before publishing changes.

**First data check:** branded queries involving reviews, license or legitimacy; About-to-admissions journeys; aggregated call dispositions where trust questions prevent an assessment. Validate which proof prospective patients actually seek.

## E4: Conflicting source answers create AI-answer risk

URLs:

- <https://www.lacatc.com/programs/medical-detox/>
- <https://www.lacatc.com/blog/what-does-medical-detox-feel-like/>

The service FAQ answers the pain question with an immediate categorical reassurance. The informational guide acknowledges possible discomfort and variable symptoms. These pages give different short answers to essentially the same patient concern. A targeted public web query retrieved both and exposed the difference in snippets. [AI-search-probe.md](ai-search-probe.md) records method and limits.

**Locator:** each page's FAQ question about pain. Short matching fragments are stored once in [checks.json](checks.json), E4 entries. This diagnosis is based on the site's own inconsistent descriptions; it makes no medical claim about what an individual will experience.

**Fix:** have clinical leadership agree on one accurate, qualified explanation, synchronize both pages and any applicable metadata/markup, and identify reviewer/date. Keep clear links to the program and next admission step. The work targets answer accuracy and confidence; it cannot promise AI citations or rank improvements.

**First data check:** run a fixed prompt set repeatedly in consumer ChatGPT search, Google AI Overviews/AI Mode and Perplexity; record date, locale, exact prompt, response and citations. This audit measured source retrieval and robots eligibility, **not consumer answer share**. Compare identifiable AI referral cohorts to qualified call/admission outcomes. Google's AI features are included in GSC Web reporting; there is no separately measured AI-overview cohort in this assessment.

## E5: Minimum admission age is unclear

URLs:

- <https://www.lacatc.com/admissions/>
- <https://www.lacatc.com/programs/residential-treatment/>
- <https://www.lacatc.com/for-families/>

Manual review of these pages' main text did not locate a minimum admission age or an explicit adult-only/teen eligibility policy. The Admissions form asks who needs help but does not resolve age fit. References to adults in national statistics or to adult dependents on other pages do not establish a facility admission policy.

**Scope:** a bounded content gap on three reviewed pages. A regex absence check in `verify_evidence.py` helps detect a later change; it does not prove semantic absence across every page, image, external listing or rendered state. The facility's actual age policy was not inferred.

**Fix:** add an approved age range and route for people outside scope near the eligibility and admissions sections. Link the same answer from family/program pages. Avoid creating age-targeted acquisition pages for services the provider does not offer.

**First data check:** age/teen/adult GSC queries plus aggregated age-ineligible call dispositions. This is ranked fifth because demand and frequency are unknown. If those signals are negligible, leave it as a small clarification rather than a content project.

## Diagnoses withheld or rejected

- All 38 fetched pages returned 200, self-canonicalized, had one H1 and exposed call links and parseable JSON-LD. These facts do not independently prove indexing, rich-result eligibility or conversion success.
- Raw markup used extra escaping in a phone-validation pattern. The rendered DOM showed normalized escaping. A claim that the form was broken was rejected; no live submission was attempted.
- The crawler initially stopped on a local DNS precheck even though the environment's HTTP proxy could resolve the public site. This was an audit-environment problem and was fixed in the crawler.
- The IOP page supplies actual morning/evening start times. A possible schedule-information gap was rejected after reading the page.
- Missing `llms.txt`, extra schema types, title length and broad keyword traffic were not used to manufacture additional priorities.
- Search bots were allowed by the retrieved robots.txt. GPTBot and OAI-SearchBot were assessed as different agents. Actual CDN bot access and consumer AI citations remain unverified.

## Technical-policy sources

- [Google: AI features and your website](https://developers.google.com/search/docs/appearance/ai-features) - ordinary search eligibility, consistent visible content/markup, no special AI schema requirement, GSC Web reporting.
- [OpenAI: crawler overview](https://developers.openai.com/api/docs/bots) - OAI-SearchBot concerns search; GPTBot has a separate purpose.

Public pages were observed, not edited. No patient information, private analytics, forms, calls or facility communications were used.
