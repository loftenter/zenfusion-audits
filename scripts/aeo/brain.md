# Zenfusion AEO Report — BRAIN

The *why* and *what* behind the Zenfusion Deep Keyword + AEO report. Pair this
with `SKILL.md` (the *how* — the operational runbook). If you only read one
thing before running a new client, read SKILL.md; if you want to understand or
extend the system, read this.

---

## 1. Philosophy

Search is splitting into two games:

- **The old game (SEO):** rank in the ten blue links. The report captures this in
  the **Top-10 Organic Competitors** block per cluster.
- **The new game (AEO — Answer Engine Optimization):** be *cited as a source*
  inside Google's AI Overview and inside LLM answers (ChatGPT, Perplexity,
  Gemini, Claude). The report captures this in the **AI Overview Wins** tab and
  the per-cluster **AI / AEO Queries** block.

Zenfusion's pitch lives in the gap between those two. The report is built to
*show* a prospect that gap with their own data: here's where you rank, here's
where you're already (or not yet) being quoted by the machines, and here's the
repeatable system to move from one to the other.

### The honesty rules (non-negotiable — they ARE the brand)

1. **Never fabricate per-LLM query volume.** No provider publishes how many
   people asked ChatGPT/Perplexity/Gemini a given prompt. Anyone selling
   "ChatGPT search volume" is modeling it. We use **real Google volume as a
   labeled proxy** and never present a made-up LLM number. The QA gate enforces
   that the AEO volume column is blank or a real integer.
2. **Async AI Overviews:** Google often returns the overview asynchronously
   (`asynchronous_ai_overview: true`), and the inline citations are then NOT in
   the API response. When that happens we mark the overview as firing and point
   to the AI Overview Wins tab — we do **not** invent a citation list.
3. **Verified vs. likely:** the AI Overview? column uses a controlled
   vocabulary — `Yes (verified)` (we pulled it live and have the cited domains),
   `Likely*` / `Maybe*` (question-intent, not yet live-checked). Only verified
   rows carry named sources. The QA gate fails the build if a verified row has
   no sources.
4. **Off-topic scrub:** cross-domain contamination (e.g. "air conditioner"
   leaking into an atmospheric-water-generator list, or "carpet pricing" into a
   water list) is filtered, and the QA gate fails the build if any survive.
5. **Derived vs. live is always labeled.** Entity columns, topical-map titles,
   and PAA "volume proxy" are clearly marked as derived/generated, not live API
   truth.

6. **Market/industry research is sourced, not invented.** Market-size, CAGR,
   and demand-driver figures in the Market Analysis doc come from actual
   `web_search` results. When named analyst firms disagree (they routinely
   do — HVAC lineset market sizing ran $8.7–$11.7B depending on the source),
   report the range and say so, the way a market-size claim reported "$8.7–
   $11.7 billion (2025)... 7.9–8.7% CAGR" rather than picking one number and
   presenting it as settled. Never round multiple conflicting estimates into
   one falsely precise figure.
7. **Competitive Analysis claims trace to live data.** Every named
   competitor's SERP position, AI-citation status, and volume in the
   Competitive Analysis doc comes from the same Stage 1 harvest that feeds
   the workbook (`competitors.json`, `aeo_live.json`, `brands.json`) — never
   from the agent's general knowledge of "who's big in this space." If a
   competitor is discussed but wasn't live-validated, say so explicitly
   rather than implying it was.

These rules are not friction; they're the reason a sophisticated buyer trusts
the deliverable. Protect them.

---

## 2. The deliverables: three documents, tab-by-tab and section-by-section

Zenfusion ships **three files** per client engagement — see `SKILL.md` for
the stage-by-stage runbook. This section covers the *content* of each.

### Document 1 — Market Analysis (docx, built first)

Industry-level context, built from live web research before any keyword API
calls. Establishes the market and the initial competitor list that Stage 0/1
will validate against live SERP data. Section order:

- **Cover page** — client name, "Market Analysis — [category/product]", a
  scope line (domain or core keyword), "[channel] | [market] | [month
  year]", "Prepared by Zenfusion | Confidential"
- **Executive Summary** — 2–3 paragraphs framing the client's position, plus
  a "HEADLINE NUMBERS" callout box (market size, CAGR, the 2–3 most
  important keyword-demand stats, in one dense line)
- **1. Market Size & Growth** — global/regional sizing with sourced ranges,
  sub-segments if the category has them
- **2. Demand Drivers** — the structural forces increasing (or suppressing)
  demand: regulatory shifts, consumer trends, platform dynamics, whatever
  actually applies to the category
- **3. Competitive Landscape** — named competitors, tiered/segmented (e.g.
  by business model or price tier), with a comparison table where useful
- **4. Buyer Segments / Target Audience** — who buys, tiered by segment, plus
  a "Search Demand by Buyer Intent" subsection once seed-keyword volumes are
  available
- **5. Key Trends & Strategic Outlook** — a named framework if one fits the
  category (e.g. the "SEO + AEO + GEO three-game" framing used for Zenfusion
  itself), then Structural Tailwinds and Risks & Constraints as bullet lists
- **6. Strategic Implications for `<client>`** — market timing, and content
  clusters prioritized once Stage 0 clusters are approved (this subsection
  can be finalized after the discovery gate even though the doc ships before
  the workbook)

### Document 2 — Deep Keyword + AEO Workbook (xlsx, built second)

The multi-tab Excel deliverable — unchanged from the original single-document
version of this skill. See the tab-by-tab breakdown below.

### Document 3 — Competitive Analysis (docx, built last)

The synthesis document — written only after the workbook has passed QA, so
every number it cites is already verified. Section order:

- **Cover page** — client name, "Competitive Analysis" (or "Competitive
  Analysis & Strategic Recommendations"), scope line, date line, "Prepared
  by Zenfusion | Confidential"
- **Executive Summary** — 2–3 paragraphs on the competitive landscape shape,
  plus a "THE CORE OPPORTUNITY" callout naming the single biggest strategic
  gap in one or two sentences (e.g. "AI engines already recommend the
  product by name, but no distributor is named as where to buy it")
- **1. Competitive Overview — Threat Rankings** — a table of named
  competitors: SERP position(s), volume, an authority signal (referring
  domains or similar), AI-cited yes/no, a threat-level tag (HIGH/MEDIUM/LOW),
  and a one-line recommended response per competitor
- **2. SERP Battlefield — Cluster by Cluster** — one subsection per cluster
  (volume, KD, who holds each top position); include a citation-source table
  for informational/review clusters (which sites AI engines and Google cite,
  by type: review site, marketplace, forum, video, government/authoritative)
- **3. AI Search (AEO/GEO) Battlefield** — the live-verified AI Overview
  citation set for the client's core queries, the gap (who's cited instead),
  and — where it applies — the operator-domain advantage: an existing
  sibling property's AI citations that can be cross-linked to lift the new
  site, with a callout making the mechanism explicit
- **4. Strategic Recommendations** — priority-ordered (Priority 1, 2, 3...),
  each tied to a specific cluster or gap identified above, each concrete
  enough to hand to a content writer (not generic SEO advice)

### Shared build mechanics for both Word docs

Both documents are built with the `docx` (npm) library per
`/mnt/skills/public/docx/SKILL.md`, using the shared
`scripts/docx_theme.js` module so every client's reports share the same
typography, table styling, callout boxes, cover-page layout, and a
header/footer with page numbers — only the palette (from
`config.json -> brand_palette`) and the content change per client. Always
render to PDF/JPEG and visually check before presenting (per the docx
skill's verification step) — a broken table or an overflowing cover page is
not acceptable in a client-facing deliverable.

---

## 2a. The workbook: tab-by-tab

Tabs render in this order. The first three are **framework tabs** (one each per
report); the rest are **cluster tabs** (one per core topic).

### ① Brand Demand
Every notable brand/product in the space with **real monthly search volume,
CPC, competition index, and YoY trend**. Ranked by volume. The client's own
brand rows are highlighted. This shows where branded demand actually sits —
yours vs. competitors. Source: `kw_data_google_ads_search_volume`.

### ② Your Demand
The client's OWN branded keywords only — brand name, domain, brand+modifier
phrases — with volume. New brands start at zero; the tab says so honestly and
frames it as the baseline to grow. Rising "Your Demand" over quarterly re-runs
is the cleanest signal that brand-building is working. This is a framework tab:
it exists even when empty, because the *movement* over time is the story.

### ③ AI Overview Wins  ← the gold
Every keyword where the client's domain(s) are cited as a source **inside
Google's AI Overview**, with volume and citation position. Source:
`dataforseo_labs_google_ranked_keywords` with `item_types=['ai_overview_reference']`.
For an established brand this is the single most persuasive asset in the report
(SoftPro's footprint: ~1,825 keywords / ~3.6M monthly searches, mostly cite
position #1). For a brand-new site it's empty for the site's own domain — in
that case we populate it from the **operator's** domains (other properties the
same company owns) and label it as "the authority you can leverage."

### Cluster tabs (one per core topic) — 8 blocks left→right
1. **Generic Keywords** (green header) — unbranded category demand: kw, vol, KD, intent, YoY.
2. **Branded Keywords** (charcoal) — terms containing a brand/retailer name.
3. **Search Segments** (blue) — keywords auto-tagged by intent modifier (install/cost/repair/etc).
4. **Top 10 Organic Competitors** (green) — the domains actually ranking for this core's head term (the *old* game).
5. **AI / AEO Queries** (blue) — up to 20 conversational queries, with AI-Overview? flag + cited sources (the *new* game).
6. **Top Reddit URLs** (charcoal) — up to 20, aggregated across ~20 secondary-keyword SERPs (not just the head term).
7. **Top YouTube Videos** (navy) — up to 20, same aggregation method.
8. **Entity Panel** (navy) — synonyms, NLP terms, derived Google/AI entities.
9. **People Also Ask** (green) — questions ranked by volume proxy.
10. **Topical Map** (navy) — ~11 sub-clusters × ~10 long-tails × click-worthy titles (~1,100 title ideas).

> Note the Reddit/YouTube methodology: to find the *top* threads/videos for a
> cluster you MUST query many secondary keywords (~20), because each keyword
> surfaces different threads. Aggregate + dedupe across all of them, rank by
> frequency, take the top 20. A single head-term pull is not enough.

---

## 3. Data sources & their quirks (DataforSEO)

| Need | Endpoint | Gotchas |
|---|---|---|
| Keyword corpus | `keyword_suggestions` | up to 1000/seed; paginate with offset |
| Brand/own volume | `kw_data_google_ads_search_volume` | **rejects punctuation** (?,.!') and **keywords >10 words**; strip before calling. Returns ~10/call reliably; batch. Empty result = volume below Google's reporting threshold (honest "—"). |
| Organic competitors | `dataforseo_labs_google_serp_competitors` | **single-keyword only in practice** (multi-keyword → 500). Rate-limits after bursts — retry transient 500s. |
| AI Overview citations (per keyword set, by domain) | `ranked_keywords` + `item_types=['ai_overview_reference']` | **the AEO Wins engine.** Caps at 1000 rows/domain; sort by volume desc to get the meaningful set. |
| Live SERP (PAA + AI Overview + Reddit + YouTube in ONE call) | `serp_organic_live_advanced` | responses are **huge** — extract only what you need, don't re-dump. Async overviews omit inline citations (see honesty rule #2). `video` + `short_videos` blocks = YouTube; organic + `discussions_and_forums` + `perspectives` = Reddit. |

The reusable AEO-wins merge logic lives in `scripts/harvest_aeo_wins.py` and
accepts saved raw responses for any number of client domains.

---

## 4. The quarterly story (why clients stay)

Re-run per client each quarter. The deltas tell the retention story:
- **Your Demand** rising = brand-building working.
- **AI Overview Wins** count/volume rising = AEO share-of-voice growing.
- New clusters entering AI Overviews = content strategy landing.

That quarter-over-quarter movement is the product, not the one-time snapshot.

---

## 5. Brand palette (Zenfusion)

Green `#35EEA0` (elevated Shopify green, the signature), Blue `#30C8EE`,
Navy `#041952`, Charcoal `#1A1A1A`. Headers use these; data rows stay clean
(no row fills except the highlight on the client's own brand/AEO rows). Palette
is set per client in `config.json → brand_palette` so the framework can be
re-skinned for white-label. The same palette drives the two Word docs via
`scripts/docx_theme.js` — one config value, three consistently-branded
deliverables. Some clients warrant a distinct accent (e.g. the Watergen/WGP
reports used a teal `#0072B5` "authority" accent instead of house blue);
pass it as `docx_theme.js`'s optional `{accent: "..."}` override rather than
changing the palette itself, so the xlsx keeps the house colors.

---

## 6. Known limitations (state them to clients)

- DataforSEO caps AEO-wins at 1000 rows/domain; the true footprint can be larger
  (the tail past ~1000 is sub-50-volume noise, so the captured set is decision-grade).
- Per-LLM volume does not exist publicly (see honesty rule #1).
- Topical-map long-tails and titles are templated/generated — review before publishing.
- Entity columns are SERP+corpus-derived, not a live Knowledge Graph / LLM API.
- YoY trend is recent-3-month vs trailing-3-month within the 12-month window — a
  directional read, labeled as such, not a strict calendar YoY.
