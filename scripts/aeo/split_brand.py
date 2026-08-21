import json, re
routed=json.load(open("routed.json"))  # cluster -> list of (kw,vol,kd,intent,yoy,cpc)

# Brand / product / manufacturer / retailer lexicon. A keyword is "branded" if it contains any of these as a word.
BRANDS = [
# own brands
"softpro","soft pro","waterdrop","water drop","quality water treatment","qwt",
# whole-house / softener competitors
"springwell","spring well","aquasana","culligan","kinetico","pelican","pentair","rheem","ge","whirlpool",
"samsung","lg","fleck","clack","genesis","aquasure","express water","home master","homemaster","nuvoh2o","nuvo",
"waterboss","kind water","kind","us water","uswater","aquaox","filtersmart","filter smart","scaleblaster","scale blaster",
"abundant flow","afwfilters","afw","durawater","dura water","iron pro","ironpro","watergen",
# POU / RO / pitcher / countertop brands
"brita","pur","zerowater","zero water","berkey","big berkey","travel berkey","apec","ispring","i spring","frizzlife",
"rkin","aquatru","aqua tru","clearly filtered","epic water","epic","aquaphor","waterdrop","drinkpod","aquasana",
"propur","pro pur","alexapure","santevia","lifestraw","life straw","sawyer","katadyn","msr","grayl","brondell",
"avalon","primo","aquasana","hydroviv","clearsource","clear source","aquagear","aqua gear","seychelle","crystal quest",
"crystalquest","waterchef","water chef","multipure","multi pure","aquasana","tier1","tier 1","pentair","everpure",
"3m","aquacrest","filterway","glacial","membrane solutions","purewell","simpure","frigidaire",
# ionizer / hydrogen / distiller brands
"tyent","kangen","enagic","life ionizer","bawell","aquavolta","echo","piurify","h2 elite","lourdes","megahome",
"durastill","mega home","waterwise","h2go","go","prime hydration",
# retailers / channels
"costco","home depot","homedepot","lowes","lowe's","amazon","walmart","menards","sam's club","sams club",
"wayfair","ebay","target","ace hardware",
]
# build word-boundary regex; sort longest first to catch multiword
BRANDS_SORTED=sorted(set(BRANDS), key=len, reverse=True)
# Some tokens are risky as bare words (ge, lg, pur, pin, go, echo, target, kind, epic, 3m, tier1). Require boundaries.
RISKY={"ge","lg","pur","go","echo","target","kind","epic","3m","pin","clack","tier 1","tier1","msr","grayl"}
pat=re.compile(r"(?<![a-z])(" + "|".join(re.escape(b) for b in BRANDS_SORTED) + r")(?![a-z])")

def is_branded(kw):
    k=kw.lower()
    m=pat.findall(k)
    if not m: return False
    # guard: if the only match is a risky short token, require it to be a standalone word (already boundaried) -- accept
    return True

split={}
for c,kws in routed.items():
    gen=[r for r in kws if not is_branded(r[0])]
    brd=[r for r in kws if is_branded(r[0])]
    split[c]={"generic":gen,"branded":brd}

# report
print(f"{'CLUSTER':32} {'GEN':>6} {'BRAND':>6}")
for c in sorted(split, key=lambda c:-(sum((r[1] or 0) for r in split[c]['generic']))):
    g=split[c]["generic"]; b=split[c]["branded"]
    print(f"{c:32} {len(g):>6} {len(b):>6}")
json.dump(split, open("split.json","w"))

# sanity: show some branded examples from a generic-heavy cluster
print("\nSample BRANDED in Water Softener:")
for r in split["Water Softener"]["branded"][:12]: print("  ",r[1],"|",r[0])
print("\nSample GENERIC in Water Softener:")
for r in split["Water Softener"]["generic"][:12]: print("  ",r[1],"|",r[0])
