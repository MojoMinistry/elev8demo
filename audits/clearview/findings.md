# Clearview: patient-inquiry workflow review

Target: https://clearviewtreatment.com/ . New-site run of the README workflow. Original LACATC assessment remains available unchanged. Use snapshot timestamps for the collection time.

## Method and scope

Command: `python3 audit.py https://clearviewtreatment.com/ --max-pages 45 --out runs/clearview`

Followed collect → detect → validate → prioritize → explain. Reviewed raw source, rendered desktop DOM on the women’s program and admissions pages, and public web retrieval of the family FAQ. GET-only; zero form submissions, calls, chats or facility contacts. Browser checks opened pages and used the Outcomes anchor; fields stayed empty. Actual connection between applicant and facility remains for the applicant to confirm.

Technical outputs: [inventory](snapshot/report.md), [HTML report](snapshot/report.html), [observations](snapshot/observations.json), [grouped candidates](snapshot/candidate_groups.json). Full third-party HTML/text remains in local gitignored runs/clearview.

## Five review priorities

### 1. Test a shorter callback route

**Evidence:** On https://clearviewtreatment.com/residential-treatment/womens-center/ the rendered HubSpot callback form presents treatment-type checkboxes, a disabled Next button until selection, and a progress indicator at page 1 of 7. The source crawl extracts only a WordPress login form; the callback loads later with JavaScript. Read-only DOM inspection found additional fields for names, birth date, insurance and address. Hidden later-step fields were inspected structurally; later steps were never completed.

**Observed:** The invitation to receive a callback leads to a seven-step intake flow in this browser. **Hypothesis:** A suitable visitor seeking initial contact may abandon a long intake. **Fix:** Experiment with a brief initial callback route, preserving necessary consent and routing; retain detailed intake for users ready for it. **First measurement:** organic landing-page form starts, step exits, completed requests, connected callbacks and qualified assessments. Compare lead quality and spam. Confidence: high on seven-step UI, medium on expected impact. Effort: moderate.

### 2. Reconcile program eligibility wording

**Evidence:** The women’s program’s inclusion section explicitly includes transgender men and AFAB nonbinary clients; its clinical-team section describes an all-female environment. The admissions FAQ describes female-identifying clients, while the family FAQ also lists a broader gender range.

URLs: https://clearviewtreatment.com/residential-treatment/womens-center/ ; https://clearviewtreatment.com/admissions/ ; https://clearviewtreatment.com/treatment-for-a-loved-one/ .

**Observed:** Descriptions of who fits the same program differ within and across pages. **Hypothesis:** Visitors and source-retrieving answer engines may receive conflicting eligibility guidance. **Fix:** Have admissions and clinical leadership approve one precise eligibility statement and propagate it to program, admissions, family and relevant schema surfaces. **First measurement:** relevant GSC query/page cohorts and aggregated eligibility-related call dispositions; fixed AI prompts with dated responses and citations. Confidence: high on wording discrepancy, medium on impact. Effort: small after policy approval.

### 3. Align insurance descriptions across older and newer pages

**Evidence:** The family FAQ describes women’s treatment through out-of-network benefits and private pay, while the women’s program page describes commercial in-network participation with program-dependent verification. Admissions supplies a more specific residential payer list and exclusions.

URLs: https://clearviewtreatment.com/treatment-for-a-loved-one/ ; https://clearviewtreatment.com/residential-treatment/womens-center/ ; https://clearviewtreatment.com/admissions/ . Family FAQ evidence came from public web retrieval; the crawler’s access result may differ.

**Observed:** The pages give different levels of specificity and network descriptions; the older FAQ could imply a narrower payment route. Actual contracts and individual coverage remain unverified. **Fix:** Benefits staff approve a program-by-payer source of truth, retain verification caveats, and update older self/family FAQs. **First measurement:** insurance-related GSC cohorts plus qualified inquiries and payer-related disqualifications. Confidence: medium; wording may reflect omitted details or historical contracts. Effort: small content change after validation.

### 4. Give outcome counters meaningful static text

**Evidence:** Women’s program source and web extraction show three outcome percentages initialized at zero. Read-only rendered DOM after using the Outcomes anchor still returned zero; data-to-value attributes specify 42, 57 and 46. The section attributes data to an Odyssey 2025 residential outcomes report. Those configured numbers were inspected as markup, with no independent validation of the underlying study.

URL: https://clearviewtreatment.com/residential-treatment/womens-center/ . Locator: `.elementor-counter-number`.

**Observed:** Text extraction exposes animation starting values rather than the configured endpoints. **Hypothesis:** Some source consumers may repeat misleading zero-valued outcomes, and some rendering states may confuse visitors. **Fix:** Render approved final values as static accessible text, add cohort/method/context links, and animate decorative presentation separately. **First measurement:** source/render consistency and accessibility QA, followed by outcomes-to-admissions journeys. Confidence: high on extraction mismatch; general browser persistence and actual AI answers remain unverified. Effort: small template change plus clinical evidence review.

### 5. Validate and provide fallbacks for virtual tours

**Evidence:** Both embedded tour frames on the women’s program page returned a client-side application error in this cloud browser. Photographic facility images remain available elsewhere on the page.

URL: https://clearviewtreatment.com/residential-treatment/womens-center/ . Locator: Virtual Tour section and its two iframe DOM snapshots.

**Observed:** This browser could not render the two tours. **Hypothesis:** Affected prospective clients lose a facility-evaluation step. **Fix:** Reproduce in ordinary desktop/mobile browsers, check the embed provider and add a direct tour link or photo fallback with a useful error state. **First measurement:** tour-load success by device/browser and facility-view-to-inquiry progression. Confidence: high for this session, low for general visitor impact. Effort: small to moderate. Treat as a validation task until reproduced.

## Access uncertainty and rejected diagnoses

Several pages returned HTTP 403 to the Python crawler while admissions rendered successfully in the cloud browser. The automated `http_error` label records the request result; each blocked URL requires access validation before any indexing or site-outage diagnosis. Public web retrieval is a separate evidence channel and may contain previously crawled content.

The callback form appeared after JavaScript loaded, so its initial absence in HTML was rejected as proof of a missing/broken form. Different phone numbers were observed changing after load, compatible with call tracking; routing and completed calls remain untested. Clearview publishes an adult age threshold, license identifier and expiry, clinical-team navigation and accreditation references, so the original LACATC gaps were not carried over. No traffic, rank, conversion loss, license validity, clinical efficacy, live AI answer share or actual payer participation was established.

## Measurement plan

Request 90 days of GSC page/query/device data and aggregate call/CRM dispositions. Prioritize admissions intent and qualified assessments/admissions. Treat tel clicks and form submissions as intermediate events. For AI consistency, record exact prompts, locale, timestamp, answers and citations across chosen consumer interfaces. This run inspected source retrieval and website content; consumer AI answers remain a follow-up.

## Evidence channels

- Python live crawl: per-response timestamps, status, redirects, hashes and snapshot paths in technical observations.
- Rendered desktop DOM: women’s program, Outcomes anchor and admissions; callback seven-step progress, delayed form, counters, tour errors, dynamic phone substitution. Field inspection was read-only.
- Public web retrieval: family FAQ payment/eligibility passages; admissions and women’s program corroboration. Retrieved pages may be cached.
- Test suite: `python3 -m unittest discover -s tests -v` — 16 passed.

Re-run technical evidence with the command above. Replay the published snapshot with `python3 audit.py --replay audits/clearview/snapshot/observations.json --out runs/clearview-replay`. The LACATC-specific verify_evidence.py script checks that original memo and should stay scoped to that site.

## Run summary

Collected 2026-10-07T15:00:17.214996+00:00 through 2026-10-07T15:03:46.102066+00:00. 38 page attempts, 5 HTTP 200 and 33 HTTP 403; 40 total HTTP requests including robots and sitemap. The 45-page ceiling was retained; the queue exhausted earlier.

## Additional technical candidate

The fetched dissociation/anxiety blog canonical points to its own path with email UTM parameters (`utm_source=hs_email&utm_medium=email`). The tool excludes query URLs, so it flags this as nonself_canonical. Confirm the intended canonical in rendered markup and GSC URL Inspection; usually publish a stable clean canonical after checking the site’s rules. This remains lower priority than admissions-entry decisions, and indexing impact is unmeasured.
