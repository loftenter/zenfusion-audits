#!/usr/bin/env python3
"""
ZENFUSION AEO — STAGE 0: URL-ONLY AUTO-DISCOVERY
=================================================
Goal: given ONLY a website URL, infer everything the pipeline needs
(seed terms, the client's own brand terms, competitor brands, and topic
clusters), then emit a discovery_review.json for a HUMAN to confirm before
any expensive harvesting or the build runs.

This stage is deliberately split into two halves because the live data calls
are made by the agent (Claude via the DataforSEO MCP, or your own code via the
DataforSEO REST API), not by this script:

  HALF A — PLAN (this script, `plan` mode):
      Reads the URL from config and prints the EXACT sequence of API calls the
      agent should make, with parameters. The agent executes them and saves
      each raw JSON response into <work>/discovery/raw/.

  HALF B — RESOLVE (this script, `resolve` mode):
      Reads those saved raw responses and produces:
        - <work>/discovery/discovery_review.json   (human-confirm file)
        - proposed clusters, seeds, own-brand terms, competitor brands
      A human edits/approves discovery_review.json; `apply` then merges the
      approved values back into config.json.

Modes:
  python3 stage0_discovery.py plan    --config <cfg>
  python3 stage0_discovery.py resolve --config <cfg>
  python3 stage0_discovery.py apply   --config <cfg>

Why this split: it keeps the agent in control of the (rate-limited, credentialed)
API while making every inferred value auditable and human-gated — which is the
"double-check before a human sees it" requirement.
"""
import json, sys, os, re
from collections import Counter

def load_cfg(p):
    cfg=json.load(open(p)); cfgdir=os.path.dirname(os.path.abspath(p)); root=cfgdir
    for _ in range(4):
        if os.path.isdir(os.path.join(root,"scripts")): break
        root=os.path.dirname(root)
    work=cfg["output"]["work_dir"]
    if not os.path.isabs(work): work=os.path.join(root,work)
    return cfg, work, p

def domain_to_seedwords(domain):
    """Heuristic seed from the domain itself: split on non-alpha + greedy dictionary
    split for concatenated lowercase domains (myhomewaterfilter -> my home water filter)."""
    base=re.sub(r"^https?://","",domain).split("/")[0].replace("www.","")
    base=base.rsplit(".",1)[0]
    # first try camelCase / separator split
    parts=re.findall(r"[a-z]+", re.sub(r"([a-z])([A-Z])", r"\1 \2", base).lower())
    # if it collapsed to one long token, greedy-split against a small common-word list
    COMMON=["water","filter","filtration","softener","reverse","osmosis","generator",
            "atmospheric","home","house","whole","system","systems","pro","pros","best",
            "purifier","conditioner","drinking","well","my","the","air","quality","clean",
            "pure","soft","hard","shower","sink","under","counter","top","fridge","ice"]
    out=[]
    for tok in parts:
        if len(tok)<=12:
            out.append(tok); continue
        # greedy longest-match dictionary split
        i=0; pieces=[]
        words=sorted(COMMON,key=len,reverse=True)
        while i<len(tok):
            for w in words:
                if tok[i:i+len(w)]==w:
                    pieces.append(w); i+=len(w); break
            else:
                i+=1  # skip a char if no match
        out.extend(pieces if pieces else [tok])
    filler={"my","the","best","online","shop","store","co","inc","llc","get","go","pro","pros","official","home","top"}
    seeds=[p for p in out if p not in filler and len(p)>2]
    return seeds or out

def plan(cfg, work):
    url=cfg["client"]["url"]; dom=cfg["client"]["domain"]
    loc=cfg["market"]["location_name"]; lang=cfg["market"]["language_code"]
    seeds_from_domain=domain_to_seedwords(dom)
    os.makedirs(os.path.join(work,"discovery","raw"), exist_ok=True)
    print("="*70)
    print(f"AUTO-DISCOVERY PLAN for {url}")
    print("="*70)
    print(f"Domain seed hint (from URL): {seeds_from_domain}")
    print("\nAGENT: make these calls and save each response to discovery/raw/<name>.json\n")
    print(f"1. get_google_ads_keyword_ideas / keyword_ideas  (page_url={url})")
    print(f"     -> save as: raw/page_ideas.json")
    print(f"     Purpose: derive the real category seed terms from the homepage content.")
    print(f"2. dataforseo_labs_google_keyword_suggestions  (keyword='<each domain seed word>', limit=200, location='{loc}', lang='{lang}')")
    print(f"     -> save as: raw/suggestions_<seed>.json  (one per seed word: {seeds_from_domain})")
    print(f"     Purpose: build the keyword corpus that clusters are derived from.")
    print(f"3. dataforseo_labs_google_ranked_keywords  (target='{dom}', item_types=['organic'], limit=200)")
    print(f"     -> save as: raw/own_ranked.json")
    print(f"     Purpose: confirm what the client already ranks for (own-brand + category footing).")
    print(f"4. dataforseo_labs_google_serp_competitors  (keywords=[<top 3-5 head terms>], limit=20)")
    print(f"     -> save as: raw/serp_competitors.json")
    print(f"     Purpose: discover the real organic competitor domains -> competitor brand list.")
    print(f"5. kw_data_google_ads_search_volume (keywords=[<domain>, '<brand phrase>' variants])")
    print(f"     -> save as: raw/own_brand_vol.json   (feeds the 'Your Demand' tab)")
    print("\nThen run:  stage0_discovery.py resolve --config <cfg>")
    # persist the seed hint for resolve
    json.dump({"seeds_from_domain":seeds_from_domain},
              open(os.path.join(work,"discovery","_plan.json"),"w"))

def _read_raw(work,name):
    p=os.path.join(work,"discovery","raw",name)
    if not os.path.exists(p): return None
    raw=json.load(open(p))
    if isinstance(raw,list) and raw and isinstance(raw[0],dict) and raw[0].get("type")=="text":
        raw=json.loads(raw[0]["text"])
    return raw

def _kw_items(raw):
    if not raw: return []
    return raw.get("items",[]) if isinstance(raw,dict) else raw

def resolve(cfg, work):
    disc=os.path.join(work,"discovery")
    rawdir=os.path.join(disc,"raw")
    # --- seeds: from page_ideas (top volume) + domain hint ---
    seeds=[]
    page=_read_raw(work,"page_ideas.json")
    for it in _kw_items(page)[:40]:
        kw=it.get("keyword") or it.get("text")
        if kw: seeds.append(kw.lower())
    # --- cluster candidates: cluster the suggestion corpus by head noun ---
    corpus=Counter()
    for fn in os.listdir(rawdir) if os.path.isdir(rawdir) else []:
        if fn.startswith("suggestions_"):
            for it in _kw_items(_read_raw(work,fn)):
                kw=(it.get("keyword") or "").lower()
                vol=(it.get("keyword_info",{}) or {}).get("search_volume") or 0
                if kw: corpus[kw]+=vol
    # naive cluster heads = most common trailing bigrams across the corpus
    head_counter=Counter()
    for kw,vol in corpus.items():
        toks=kw.split()
        if len(toks)>=2:
            head_counter[" ".join(toks[-2:])]+=1
    cluster_candidates=[{"label":h.title(),"head_keyword":h} for h,_ in head_counter.most_common(25)]
    # --- competitor brands: domains from serp_competitors ---
    comps=[]
    sc=_read_raw(work,"serp_competitors.json")
    for it in _kw_items(sc)[:25]:
        d=it.get("domain")
        if d and not any(x in d for x in ["google.","reddit.","youtube.","wikipedia.","amazon.","homedepot.","lowes."]):
            comps.append(d)
    # --- own brand terms: domain + spaced variant ---
    dom=cfg["client"]["domain"]; base=dom.rsplit(".",1)[0]
    spaced=re.sub(r"([a-z])([A-Z])",r"\1 \2",base)
    own=[base.lower(), spaced.lower()]
    review={
      "_INSTRUCTIONS":"HUMAN REVIEW REQUIRED. Edit any field, delete wrong entries, then run: stage0_discovery.py apply --config <cfg>. Nothing is written to config.json until you approve here.",
      "client_domain":dom,
      "proposed_seed_terms": sorted(set(seeds))[:5] or domain_to_seedwords(dom),
      "proposed_own_brand_terms": own,
      "proposed_competitor_brands": comps[:24],
      "proposed_clusters": cluster_candidates,
      "confidence_notes":{
        "seed_terms":"from homepage keyword ideas; verify they match the business",
        "clusters":"auto-grouped by trailing bigram frequency; MERGE/RENAME as needed — this is the roughest auto-step",
        "competitors":"organic SERP domains with marketplaces/aggregators stripped; confirm these are true competitors",
      }
    }
    os.makedirs(disc, exist_ok=True)
    json.dump(review, open(os.path.join(disc,"discovery_review.json"),"w"), indent=2)
    print(f"Wrote {os.path.join(disc,'discovery_review.json')}")
    print(f"  seeds: {len(review['proposed_seed_terms'])} | clusters: {len(review['proposed_clusters'])} | competitors: {len(review['proposed_competitor_brands'])}")
    print("  -> HUMAN: review/edit that file, then run `apply`.")

def apply(cfg, work, cfg_path):
    review=json.load(open(os.path.join(work,"discovery","discovery_review.json")))
    cfg["discovery"]["seed_terms"]=review["proposed_seed_terms"]
    cfg["discovery"]["mode"]="full"  # now resolved
    cfg["brands"]["own_brand_terms"]=review["proposed_own_brand_terms"]
    cfg["brands"]["competitor_brands"]=review["proposed_competitor_brands"]
    cfg["clusters"]=review["proposed_clusters"]
    json.dump(cfg, open(cfg_path,"w"), indent=2)
    print(f"Applied approved discovery values to {cfg_path}")
    print(f"  {len(cfg['clusters'])} clusters, {len(cfg['brands']['competitor_brands'])} competitors, {len(cfg['discovery']['seed_terms'])} seeds")

def main():
    if len(sys.argv)<4 or sys.argv[2]!="--config":
        print("usage: stage0_discovery.py [plan|resolve|apply] --config <path>"); sys.exit(2)
    mode=sys.argv[1]; cfg,work,cfg_path=load_cfg(sys.argv[3])
    os.makedirs(work, exist_ok=True)
    if mode=="plan": plan(cfg,work)
    elif mode=="resolve": resolve(cfg,work)
    elif mode=="apply": apply(cfg,work,cfg_path)
    else: print("unknown mode"); sys.exit(2)

if __name__=="__main__":
    main()
