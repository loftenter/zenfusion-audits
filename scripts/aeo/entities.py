import json, re
from collections import Counter
routed=json.load(open("routed.json"))

STOP=set("the a an of for to in on with and or your you my best top how what is are vs review reviews price cost buy near me system systems filter filters water home house can do does it that this".split())

# Known entity lexicon for derivation (brands/orgs/materials/standards/product-types) — these are the
# kinds of nodes Google's Knowledge Graph / NLP entity tagger recognizes in this niche.
BRANDS=["SoftPro","WaterDrop","SpringWell","Aquasana","Culligan","Kinetico","Pelican","Pentair","Brita","PUR","ZeroWater","Berkey","APEC","iSpring","Frizzlife","RKIN","AquaTru","Clearly Filtered","Kind Water Systems","US Water Systems","GE","Whirlpool","Samsung","LG","Fleck","Genesis","Aquasure","Express Water","Home Master","NuvoH2O","Epic Water","Waterboss","Rheem","Tyent","Kangen","Life Ionizer","Santevia","ProPur","Alexapure"]
ORGS=["NSF","EPA","WQA","ANSI","FDA","CDC","Water Quality Association","NSF/ANSI 53","NSF/ANSI 42","NSF/ANSI 58"]
MATERIALS=["activated carbon","catalytic carbon","KDF","reverse osmosis membrane","ion exchange resin","coconut shell carbon","carbon block","sediment media","calcite","greensand","birm","zeolite","polypropylene"]
CONTAMINANTS=["PFAS","PFOA","PFOS","lead","fluoride","chlorine","chloramine","iron","manganese","arsenic","nitrate","sulfur","hardness","calcium","magnesium","sediment","tannins","bacteria","microplastics","chromium-6","TDS","VOCs"]
PRODUCTTYPES=["reverse osmosis system","water softener","whole house filter","under-sink filter","countertop filter","water filter pitcher","faucet filter","UV purifier","water distiller","ionizer","sediment filter","iron filter","salt-free conditioner"]

def tokens(kws):
    c=Counter()
    for kw,*_ in kws:
        for w in re.findall(r"[a-z0-9\-]+", kw.lower()):
            if w in STOP or len(w)<3: continue
            c[w]+=1
    return c

def bigrams(kws):
    c=Counter()
    for kw,*_ in kws:
        ws=[w for w in re.findall(r"[a-z0-9\-]+", kw.lower()) if w not in STOP and len(w)>2]
        for i in range(len(ws)-1):
            c[ws[i]+" "+ws[i+1]]+=1
    return c

def derive(cluster, kws):
    text=" ".join(k[0].lower() for k in kws)
    # synonyms: top alternate core phrasings (bigrams/trigrams mentioning the theme), distinct from core
    big=bigrams(kws)
    syn=[b for b,_ in big.most_common(40)]
    # NLP terms: most frequent meaningful single tokens
    tok=tokens(kws)
    nlp=[w for w,_ in tok.most_common(25)]
    # Google entities: brands/orgs/materials/contaminants/producttypes actually present in corpus
    def present(lst): return [e for e in lst if re.search(r"\b"+re.escape(e.lower())+r"\b", text)]
    g_brands=present(BRANDS); g_orgs=present(ORGS); g_mat=present(MATERIALS)
    g_cont=present(CONTAMINANTS); g_pt=present(PRODUCTTYPES)
    google_ents = g_brands[:12] + g_orgs[:6] + g_pt[:8] + g_mat[:6] + g_cont[:10]
    # AI entities: broader associated concepts (derived) — union of contaminants+standards+use-cases+adjacent concepts
    ai_concepts = list(dict.fromkeys(
        g_cont[:10] + g_orgs[:5] +
        [c for c in ["hard water","well water","city water","municipal water","drinking water","point of use","point of entry",
                     "water testing","TDS meter","remineralization","backwash","resin regeneration","micron rating",
                     "flow rate","GPM","filter lifespan","water hardness (GPG)","off-grid","emergency preparedness"]]
    ))
    return syn, nlp, google_ents, ai_concepts

out={}
for c,kws in routed.items():
    syn,nlp,ge,ai=derive(c,kws)
    out[c]={"keywords":kws,"synonyms":syn,"nlp":nlp,"google_entities":ge,"ai_entities":ai}

json.dump(out, open("enriched.json","w"))
# quick preview
for c in ["Water Softener","Reverse Osmosis","Iron Filter"]:
    e=out[c]
    print("\n===",c,"===")
    print("synonyms:",e["synonyms"][:8])
    print("nlp:",e["nlp"][:10])
    print("google_entities:",e["google_entities"][:12])
    print("ai_entities:",e["ai_entities"][:10])
