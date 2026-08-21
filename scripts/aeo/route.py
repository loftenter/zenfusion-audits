import json, re
corpus=json.load(open("corpus.json"))  # (kw,vol,kd,intent,yoy,cpc)

# Cluster routing rules — ordered, first match wins. Mirrors the workbook's cluster set.
# Each: (cluster_key, [must-contain-any], [exclude-any])
RULES = [
 ("Brand & Competitor", ["softpro","waterdrop","springwell","aquasana","culligan","kinetico","pelican","pentair","brita","pur ","zerowater","zero water","berkey","apec","ispring","frizzlife","rkin","aquatru","clearly filtered","kind water","us water","ge ","whirlpool","samsung","lg ","waterboss","fleck","genesis water","aquasure","express water","home master","nuvoh2o","nuvo","aquaox","filtersmart","drinkpod","epic water","clearlyfiltered","life ionizer","tyent","kangen","santevia","propur","big berkey","alexapure","waterdrop"], []),
 ("Reverse Osmosis", ["reverse osmosis","osmosis","ro system","ro water","ro filter","ro membrane"," ro ","tankless ro"], []),
 ("Under-Sink", ["under sink","under-sink","under counter","under-counter","under the sink","undersink"], ["reverse osmosis","osmosis"]),
 ("Countertop & Pitcher", ["countertop","counter top","pitcher","jug","gravity","dispenser"], []),
 ("Faucet & Inline", ["faucet","tap filter","tap water filter","inline","in-line","shower"], []),
 ("Refrigerator/Fridge", ["refrigerator","fridge","ice maker"], []),
 ("Iron Filter", ["iron"], ["softpro","waterdrop"]),
 ("Fluoride Filter", ["fluoride"], []),
 ("PFAS / Lead", ["pfas","forever chemical","lead","arsenic","nitrate","chromium"], []),
 ("Chlorine / Chloramine", ["chlorine","chloramine","dechlor"], []),
 ("Carbon / Media", ["carbon","kdf","catalytic","activated"], []),
 ("Sediment & Specialty Well", ["sediment","tannin","sulfur","manganese","acid neutralizer","calcite","rust","turbidity"], []),
 ("UV / Disinfection", ["uv ","ultraviolet","u.v","bacteria","virus","microbio"], []),
 ("Water Distiller", ["distiller","distilled","distillation"], []),
 ("Alkaline / Ionizer / Hydrogen", ["alkaline","ionizer","ionized","hydrogen water","ph water"], []),
 ("Water Softener", ["softener","soften","salt free","salt-free","saltless","descaler","water conditioner","hard water"], []),
 ("Well Water", ["well water","well filter","filter for well","well system"], []),
 ("Whole House / POE", ["whole house","whole home","whole-house","whole of house","point of entry","house water filter","home water filtration","house filter"], []),
 ("Water Purifier", ["purifier","purification","purify"], []),
 ("Water Filtration System", ["filtration system","filtration systems"], []),
 ("Water Filter System", ["filter system","filter systems"], []),
 ("Best / Reviews / Compare", ["best ","review","vs ","comparison","top 10","top 5","rated"], []),
 ("Price / Cost / Buy", ["price","cost","cheap","for sale","buy ","deal","near me","installation cost"], []),
 ("Home / Residential", ["for home","home water filter","residential","house"], []),
 ("Water Filter (head)", ["water filter","filter water"], []),
]

def route(kw):
    k=" "+kw.lower()+" "
    for cluster, inc, exc in RULES:
        if any(x in k for x in inc) and not any(x in k for x in exc):
            return cluster
    return "Water Filter (head)"

clusters={}
for kw,vol,kd,intent,yoy,cpc in corpus:
    clusters.setdefault(route(kw),[]).append((kw,vol,kd,intent,yoy,cpc))

# sort each by volume, dedupe
for c in clusters:
    seen={}
    for r in sorted(clusters[c],key=lambda r:-(r[1] or 0)):
        if r[0] not in seen: seen[r[0]]=r
    clusters[c]=list(seen.values())

# report
rows=sorted(clusters.items(), key=lambda kv:-sum((r[1] or 0) for r in kv[1]))
total=0
for c,its in rows:
    tv=sum((r[1] or 0) for r in its); total+=len(its)
    print(f"{len(its):>4} kw | ~{tv:>9,}/mo | {c}")
print("TOTAL keywords routed:",total)
json.dump({c:its for c,its in clusters.items()}, open("routed.json","w"))
