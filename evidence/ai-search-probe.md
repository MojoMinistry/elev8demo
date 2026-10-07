# AI-source retrieval spot check

**Date:** October 7, 2026. **Interface:** web-search tool used by OpenAI Codex in ChatGPT Work Mode. **Purpose:** check which public source passages can be retrieved for a patient question and whether they agree.

## Observed query and result

Exact query: `site:lacatc.com "detox" "painful"`

The returned results included:

1. <https://www.lacatc.com/blog/what-does-medical-detox-feel-like/> - snippet acknowledged discomfort and variability.
2. <https://www.lacatc.com/programs/medical-detox/> - snippet exposed a categorical reassurance in the program FAQ.

Both source pages had also been fetched directly by the crawler, and the corresponding text was checked against the saved HTML-derived observations. Their short, literal evidence anchors are in `checks.json`; the report paraphrases the contrast.

A second query, `site:lacatc.com "Medi-Cal" "covered"`, returned general Medi-Cal pages in this tool. That result was insufficient to establish anything about the facility's indexing or AI visibility and was excluded from the findings.

## What this establishes

The conflicting source answers are retrievable by an AI-assisted search workflow. The website's own short answers could steer a generated response toward different expectations. This is a concrete answer-consistency problem worth fixing before measuring AI-referred patient inquiries.

The crawl also read robots.txt: the sampled URLs were allowed for Googlebot, OAI-SearchBot and PerplexityBot. This only describes the retrieved rules, not actual production crawler access through a CDN.

## What remains unmeasured

No consumer ChatGPT session, Google AI Overview, AI Mode response, or Perplexity answer was captured. No share-of-voice, citation rank, actual synthesized error, or lost admission was measured. Search results and an auditing assistant's interpretation are different evidence from a consumer AI answer.

## Follow-up protocol

Use a fixed small prompt set in clean sessions, with the same stated locale and date. Examples: whether detox at the named facility can be painful; which services a specific plan may cover at the facility; which ages it accepts; where to verify its credentials. Run each prompt at least three times per product. Record exact response, facility mention, source URL, factual qualification, date and locale. Save screenshots only for actual observed answers. Distinguish a feature that did not trigger from a triggered answer that omitted the facility.

After approved source edits, repeat the same prompts and compare factual accuracy and citations. Treat small samples as directional. Pair identifiable AI referrals with answered/qualified calls and admissions; avoid assigning all Google Web traffic to AI features.
