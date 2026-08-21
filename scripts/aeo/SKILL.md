---
name: zenfusion-aeo
description: Use this skill whenever the user wants to produce a Zenfusion client report for any website — the THREE-DOCUMENT deliverable (Market Analysis docx → Deep Keyword + AEO Excel workbook → Competitive Analysis docx) that shows a brand's position in classic Google search AND the AI-answer (AEO) layer. Trigger on phrases like "run the Zenfusion report for [client/domain]", "/zenfusion-aeo [url]", "build the Zenfusion deck for [site]", "Deep Keyword + AEO analysis", "stage 0 / stage 1 harvest", or any mention of stage0_discovery, harvest_aeo_wins, build_paa, or qa_check. Also trigger when the user uploads a Zenfusion config.json, asks to onboard a new client into the Zenfusion pipeline, or wants to QA-gate a finished workbook before delivery. ALWAYS produce all three deliverables (Market Analysis, workbook, Competitive Analysis) unless the user explicitly asks for only one of them by name. Requires the DataforSEO MCP connector for Stage 0/1 (URL discovery + live harvest) and the docx skill for the two Word deliverables; the workbook build/QA stages run locally with no API.
---

# Zenfusion Client Report — SKILL (operational runbook)

How to produce one client's **full three-document deliverable**, start to
finish. Read `brain.md` for the *why*; this is the *how*. Written so a fresh
Claude session (with the DataforSEO MCP connected) or a developer can run it.

## The non-negotiable: three deliverables, every run

Every Zenfusion client engagement ships **three files**, in this order:

1. **Market Analysis** (`.docx`) — industry sizing, demand drivers, named
   competitors, buyer segments, trends, strategic implications. Built FIRST,
   from live web research — before any keyword API calls — because it's what
   surfaces and frames the competitor list the workbook will validate.
2. **Deep Keyword + AEO Workbook** (`.xlsx`) — the multi-tab Excel deliverable
   (Stages 0–3 below). Built second, once the market research has produced a
   validated competitor/cluster list.
3. **Competitive Analysis** (`.docx`) — named-competitor threat rankings,
   cluster-by-cluster SERP battlefield, AEO/GEO citation gap, and a
   prioritized action plan. Built LAST, because it draws on both the market
   research AND the live keyword/AEO data — it is the synthesis document.

**Do not stop after the workbook.** A run that produces only the `.xlsx` is
an incomplete delivery unless the user has explicitly said they only want the
workbook this time. If a user says "just run the AEO report," that still
means all three — "AEO report" is Zenfusion's name for the whole deliverable,
not the workbook alone. Only skip a document if the user names it explicitly
("just the workbook," "skip market analysis," "I only need competitive").

## What's automated vs. agent-driven (read this first)

| Stage | Deliverable | Who runs it | How |
|---|---|---|---|
| A — Business context + Market Analysis | `Market Analysis.docx` | **Agent**: web_fetch site, web_search industry data, write + build docx | see "Stage A" below |
| 0 — URL-only discovery | *(feeds workbook)* | **Agent** makes the API calls; **human** approves | `stage0_discovery.py plan/resolve/apply` |
| 1 — Harvest (corpus, brands, AEO wins, reddit/youtube, AEO live) | *(feeds workbook)* | **Agent** (Claude via MCP, or your code via DataforSEO REST) | live API calls → save JSON into `data/` |
| 2 — Build workbook | `<client> Deep Keyword Analysis.xlsx` | **Fully automated** | `build_paa.py --config` |
| 3 — QA gate | *(gates the workbook)* | **Fully automated** | `qa_check.py --config` |
| 4 — Competitive Analysis | `Competitive Analysis.docx` | **Agent**: synthesize market + workbook data, write + build docx | see "Stage 4" below |

Stages 2–3 are pure local Python (no API) and fully reproducible. Stages
A, 0, 1, and 4 need an agent (live research, live API access, or original
written synthesis), so an agent drives them — this is by design, not a gap.
The orchestrator (`run.py`) covers Stages 0–3 only; Stages A and 4 are
chat-native (web research + the docx skill) and are not shell scripts,
because their content must be freshly researched/written per client, never
templated.

## Package layout

```
zenfusion_aeo/
  run.py                       orchestrator (workbook stages 0-3 only)
  brain.md                     methodology — read this for doc outlines
  SKILL.md                     this file
  scripts/
    build_paa.py               workbook builder (config mode: --config)
    qa_check.py                QA gate (--config)
    stage0_discovery.py        URL-only auto-discovery (plan/resolve/apply)
    harvest_aeo_wins.py        merges AEO-wins raw responses across domains
    topical_engine.py          topical-map generator
    segment_engine.py          intent-segment tagger
    docx_theme.js              SHARED styling module for the two Word docs —
                                require() this from your build script so every
                                client's Market/Competitive Analysis uses the
                                same fonts, tables, callouts, cover page, and
                                header/footer-with-page-numbers. Palette comes
                                from config.json -> brand_palette.
  clients/
    _example_config.json       copy this for a new client
    <client>/
      config.json               the ONLY per-client file you edit
      data/                     agent-produced JSON (the harvest output)
      discovery/                (url_only mode) raw API responses + review file
      Market Analysis.docx      deliverable 1
      <output>.xlsx             deliverable 2
      Competitive Analysis.docx deliverable 3
      qa_report.json            machine-readable QA result (workbook only)
```

## Quick start — new client (you already know the business, or just have a URL)

Trigger phrase: **`/zenfusion-aeo <domain>`** or "run the Zenfusion report
for `<domain>`". No intake form required — the agent derives business
context from the site itself.

1. `cp clients/_example_config.json clients/<client>/config.json`; fill in
   what you already know, or leave `discovery.mode="url_only"` and let
   Stage A / Stage 0 populate it (see below).
2. **Stage A — Market Analysis** (below). Produces `Market Analysis.docx`
   and, as a byproduct, a validated competitor list.
3. **Stage 0 — Discovery.** If `discovery.mode="url_only"`:
   `stage0_discovery.py plan/resolve/apply` (human approves clusters).
   If `mode="full"` and clusters/brands are already set in config.json,
   skip straight to Stage 1.
4. **Stage 1 — Harvest** (below) → fills `clients/<client>/data/`.
5. `python3 run.py --config clients/<client>/config.json` → builds workbook
   + QA-gates it. On CLEAN PASS the xlsx is cleared for human review.
6. **Stage 4 — Competitive Analysis** (below). Produces
   `Competitive Analysis.docx` using the market research + live workbook data.
7. Present all three files together.

## Stage A — Market Analysis (agent-driven, FIRST)

1. **Business context.** `web_fetch` the client's homepage + product/catalog
   page. `web_search` for the brand, operator/parent domains, press
   coverage, and competitor mentions. Extract: what they sell, pricing,
   positioning, own-brand terms, likely operator domains, market/language.
   Save the durable facts to the client's memory file (`/areas/<client>.md`)
   as you go.
2. **Industry research.** 3–6 targeted `web_search` calls: market size/CAGR
   for the category, the client's core demand drivers (regulatory, consumer
   trend, platform shift — whatever applies), named competitors in the
   space, and current search-behavior trends relevant to the category. When
   analyst estimates disagree, report the range and say so explicitly — see
   the honesty rules in `brain.md`. Do not fabricate a single precise number
   where sources conflict.
3. **Derive the competitor list** from this research — this feeds Stage 0's
   `competitor_brands` / `operator_domains` and gets validated later against
   live SERP data (`serp_competitors`) once harvest runs. Note explicitly in
   the doc that competitor rankings will be validated against live data in
   the Competitive Analysis.
4. **Write the document.** Structure (see `brain.md` §2 for the full outline
   with examples):
   - Cover page (client name, "Market Analysis — [category/product]", scope
     line, "[channel] | [market] | [month year]", "Prepared by Zenfusion |
     Confidential")
   - Executive Summary (2–3 paragraphs + a "HEADLINE NUMBERS" callout)
   - 1. Market Size & Growth
   - 2. Demand Drivers
   - 3. Competitive Landscape (named competitors, positioning)
   - 4. Buyer Segments / Target Audience
   - 5. Key Trends & Strategic Outlook (tailwinds + risks)
   - 6. Strategic Implications for `<client>` (finalize once Stage 0
     clusters are approved — this section should reference the approved
     cluster list, so it's fine to draft it last even though the doc ships
     before the workbook)
5. **Build the docx.** `view /mnt/skills/public/docx/SKILL.md` first (page
   size, table, and bullet gotchas). Then:
   ```js
   const T = require('./scripts/docx_theme.js')(config.brand_palette);
   // T.h1/h2/h3/body/bullet/spacer/pb/callout/dataTable/coverPage/buildDoc
   ```
   Save as `clients/<client>/Market Analysis.docx`. Render to PDF/JPEG and
   visually check it (per the docx skill's "Verify the output" step) before
   moving on.

## Stage 0 — URL-only discovery

```
python3 scripts/stage0_discovery.py plan    --config clients/<client>/config.json
python3 scripts/stage0_discovery.py resolve --config clients/<client>/config.json
```
Human reviews/edits `discovery/discovery_review.json` (clusters especially —
the auto-grouping is the roughest step), then:
```
python3 scripts/stage0_discovery.py apply --config clients/<client>/config.json
```
merges approved values into `config.json`, flips mode to `full`.

## Stage 1 — the harvest (agent-driven), step by step

Produce these files in `clients/<client>/data/`. Required: `split.json`,
`enriched.json`, `paa_all.json`, `brands.json`, `yourdemand.json`,
`aeo_wins.json`. Optional but recommended: `competitors.json`, `aeo.json`,
`reddit_yt.json`, `aeo_live.json`.

1. **Keyword corpus** — `keyword_suggestions` on each seed term (limit 1000,
   paginate). Route into clusters; split generic vs. branded (brand-name match).
   → `split.json` (per cluster: generic[], branded[]), `enriched.json` (entities).
2. **Brand Demand** — `kw_data_google_ads_search_volume` on the competitor brand
   list (strip punctuation, ≤10 words, batch ~10/call). Compute YoY from the
   12-month series. → `brands.json` (rows sorted by volume desc).
3. **Your Demand** — same endpoint on `own_brand_terms` + domain variants.
   → `yourdemand.json` (`{brand_name, checked:[[kw,type,vol,cpc,comp],...]}`).
   All-null is the correct, honest result for a new brand.
4. **AI Overview Wins** — for the client domain AND each `operator_domains`
   entry, call `ranked_keywords` with `item_types=['ai_overview_reference']`,
   `limit=1000`, `order_by` volume desc. Save each raw response, then:
   `python3 scripts/harvest_aeo_wins.py data/aeo_wins.json off_topic.txt "dom1::raw1.json" "dom2::raw2.json"`
   (off_topic.txt = the config's `off_topic_scrub` list, one per line).
5. **Per cluster** (repeat for each):
   - **Competitors:** `dataforseo_labs_google_serp_competitors` on the head
     keyword (single keyword; retry 500s) → `competitors.json[cluster]`.
     This is also where you validate the Stage A market-research competitor
     list against live SERP data — note any surprises for the Competitive
     Analysis (a market-research-named competitor who isn't actually ranking,
     or a live SERP competitor market research missed).
   - **Reddit/YouTube + live AEO:** pick ~20 distinct secondary keywords for the
     cluster, call `serp_organic_live_advanced` on each. From each response
     extract: AI Overview citations → `aeo_live.json[query]`; reddit URLs and
     YouTube videos → `reddit_yt.json[cluster]`. Dedupe; the builder caps at 20.
   - **AI queries + PAA + topical** are assembled from the corpus/PAA into
     `aeo.json` and `paa_all.json` (questions per cluster).

> Tip: `serp_organic_live_advanced` returns AI-Overview citations, Reddit, AND
> YouTube in ONE call — so the ~20 secondary-keyword pulls per cluster feed all
> three blocks at once. Extract compact fields immediately; the raw payloads are
> very large.

## Stage 2 — build

```
python3 scripts/build_paa.py --config clients/<client>/config.json
```
Reads `data/*.json` by convention, writes the xlsx into `work_dir`. No API.

## Stage 3 — QA gate (the accuracy guarantee)

```
python3 scripts/qa_check.py --config clients/<client>/config.json
```
14 checks: tabs present, off-topic scrub clean, no fabricated LLM volume, AEO
vocabulary controlled, brand volumes numeric, AEO-wins reconcile, reddit/youtube
valid + within cap, no column collisions, verified-AEO rows have sources.
- **CLEAN PASS** → cleared for human review.
- **PASS WITH WARNINGS** → safe to present; flag warnings to the reviewer.
- **FAIL** → exits non-zero, writes `qa_report.json`; do NOT present to a human.

The agent should treat a non-zero exit from `run.py` as a hard stop and surface
`qa_report.json` rather than handing a broken report to the team.

## Stage 4 — Competitive Analysis (agent-driven, LAST)

Only start this once the workbook has a CLEAN PASS or PASS WITH WARNINGS —
this document quotes live numbers from it and needs them to be QA-verified.

1. **Pull the numbers you need** from the finished workbook and `data/*.json`:
   per-cluster head-term SERP competitors and their positions, AI Overview
   Wins totals (and the biggest individual wins), brand demand for named
   competitors, and reddit/YouTube citation sources per cluster.
2. **Write the document.** Structure (see `brain.md` §2 for the full outline
   with examples):
   - Cover page (client name, "Competitive Analysis" or "Competitive
     Analysis & Strategic Recommendations", scope line, date line, "Prepared
     by Zenfusion | Confidential")
   - Executive Summary (2–3 paragraphs + a "THE CORE OPPORTUNITY" callout —
     name the single biggest strategic gap in one or two sentences)
   - 1. Competitive Overview — Threat Rankings (a `dataTable` of named
     competitors: position/rank, volume, authority signal, AI-cited?
     yes/no, threat level, recommended response)
   - 2. SERP Battlefield — Cluster by Cluster (one `h2` per cluster: volume,
     KD, who holds each of the top positions, a source-citation table where
     relevant)
   - 3. AI Search (AEO/GEO) Battlefield — what's cited today for the
     client's core queries and by whom (verified live-SERP citations only,
     never invented); if there's an operator-domain AEO advantage, this is
     the section to feature it, with a callout
   - 4. Strategic Recommendations — priority-ordered, specific, tied to the
     cluster/gap that motivates each one (not generic SEO advice)
3. **Build the docx** the same way as Stage A, reusing `docx_theme.js` and
   the SAME `config.brand_palette` so the two documents visually match.
   Save as `clients/<client>/Competitive Analysis.docx`. Verify by rendering
   to PDF/JPEG before presenting.

## Agent operating contract (for the auto-run version)

When a Zenfusion agent runs this from just a URL:
1. Fetch the site + research the business (Stage A step 1). Build config
   (URL-only if needed).
2. Run industry research and write `Market Analysis.docx` (Stage A steps
   2–5), deriving the initial competitor/cluster candidates.
3. Run Stage 0 discovery; **pause and present `discovery_review.json` to a
   human** for confirmation. Do not proceed to harvest on unconfirmed
   clusters/competitors.
4. After apply, run the Stage-1 harvest, saving JSON into `data/`. Validate
   the Stage A competitor list against live SERP results here.
5. Run `run.py` (Stages 2–3). If QA FAILs, fix the flagged issue and
   re-run; never present a FAIL to the team.
6. Write `Competitive Analysis.docx` (Stage 4), using both documents' data.
7. Present all three files (Market Analysis.docx, the xlsx, Competitive
   Analysis.docx) + a one-paragraph summary of the headline numbers (AEO
   Wins total, Brand Demand leader, Your Demand baseline, the single biggest
   competitive gap) for human review.

Double-check before hand-off: confirm all three files exist, tab count and
AEO-wins total on the workbook, and a spot-check of one cluster's
Reddit/YouTube/AEO rows and one Competitive Analysis claim against the
source data — every number in the Word docs should trace back to something
in `data/*.json`, the live workbook, or a cited web search, never invented.
