#!/usr/bin/env python3
"""
ZENFUSION FRAMEWORK — AI Overview Wins harvester.

Pulls every keyword where a client's domain(s) are cited as a source inside
Google's AI Overview, via DataforSEO Labs ranked_keywords (item_type =
ai_overview_reference). Merges across multiple client domains, dedupes,
scrubs off-topic cross-matches, and writes aeo_wins.json for build_paa.py.

This is the engine behind the "③ AI Overview Wins" tab. Re-run per client,
per quarter, to track AEO share-of-voice over time.

USAGE (the actual DataforSEO calls are made by the operator/agent and the raw
JSON responses saved to disk; this script merges them):

  python3 harvest_aeo_wins.py out.json off_topic.txt raw1.json raw2.json ...

Each rawN.json is a saved DataforSEO ranked_keywords response (the MCP wrapper
format with [{"type":"text","text":"<json string>"}] OR the plain API JSON).
off_topic.txt is a newline list of substrings to scrub (cross-domain terms).
"""
import json, sys, re

def load_raw(path):
    """Accepts either the MCP-wrapped [{'type':'text','text':'...'}] form or plain API JSON."""
    raw = json.load(open(path))
    if isinstance(raw, list) and raw and isinstance(raw[0], dict) and raw[0].get("type") == "text":
        raw = json.loads(raw[0]["text"])
    return raw.get("items", [])

def extract_rows(items, domain_label):
    rows = []
    for it in items:
        kw = it.get("keyword_data", {}).get("keyword")
        vol = (it.get("keyword_data", {}).get("keyword_info", {}) or {}).get("search_volume") or 0
        el = it.get("ranked_serp_element", {}).get("serp_item", {}) or {}
        pos = el.get("rank_absolute")
        if kw:
            rows.append((kw, vol, pos, domain_label))
    return rows

def main():
    out_path = sys.argv[1]
    off_path = sys.argv[2]
    raw_specs = sys.argv[3:]  # each "domain_label::path"

    off = []
    try:
        off = [l.strip().lower() for l in open(off_path) if l.strip()]
    except FileNotFoundError:
        pass

    merged = {}
    for spec in raw_specs:
        label, path = spec.split("::", 1)
        for kw, vol, pos, dom in extract_rows(load_raw(path), label):
            if kw in merged:
                merged[kw]["domains"].add(dom)
                if pos is not None:
                    merged[kw]["pos"] = min(merged[kw]["pos"], pos) if merged[kw]["pos"] else pos
            else:
                merged[kw] = {"kw": kw, "vol": vol, "pos": pos, "domains": {dom}}

    rows = []
    for r in merged.values():
        if any(o in r["kw"].lower() for o in off):
            continue
        rows.append([r["kw"], r["vol"], r["pos"], " + ".join(sorted(r["domains"]))])
    rows.sort(key=lambda x: -x[1])
    json.dump(rows, open(out_path, "w"))

    print(f"AEO Wins: {len(rows)} keywords | {sum(r[1] for r in rows):,} mo vol | "
          f"{sum(1 for r in rows if r[2]==1)} at pos 1 | "
          f"{sum(1 for r in rows if '+' in r[3])} cited by multiple domains")

if __name__ == "__main__":
    main()
