# Dynamic, industry-agnostic search-segment tagger.
# Detects modifier families from the keyword corpus itself, no hardcoded industry assumptions.
import json, re
from collections import Counter

# A library of GENERIC search-modifier families defined by trigger tokens. These are cross-industry
# (commerce + service + research patterns). The engine only SURFACES families that actually appear
# with volume in the given corpus, so a plumbing client lights up repair/install, a SaaS client lights
# up free/login/pricing, etc. Order = priority when a kw matches multiple.
FAMILIES = [
 ("DIY / Build", ["diy","do it yourself","homemade","build","make your own","how to make","how to build","kit "]),
 ("Installation / Installer", ["install","installation","installer","setup","set up","hook up","plumber","fitting","mount"]),
 ("Cost / Price", ["cost","price","pricing","how much","cheap","budget","affordable","quote","estimate"]),
 ("Repair / Service", ["repair","fix","troubleshoot","not working","problem","service","maintenance","leaking","broken"]),
 ("Replacement / Parts", ["replacement","replace","parts","cartridge","filter change","refill","spare","component"]),
 ("Reviews / Ratings", ["review","reviews","rating","rated","complaints","worth it","reddit","consumer reports"]),
 ("Comparison / vs", [" vs ","versus","compare","comparison","difference between","alternative"]),
 ("Best / Top", ["best ","top ","top 10","top 5","highest rated","recommended"]),
 ("Near Me / Local", ["near me","near you","local","in my area"," nearby"]),
 ("Salt / Salt-Free", ["salt free","salt-free","saltless","salt based","with salt","no salt","potassium"]),
 ("Size / Capacity", ["grain","gpm","gallon","capacity"," size","sizing","how many","cubic","liter","litre"]),
 ("Solar / Off-Grid", ["solar","off grid","off-grid","battery","renewable"]),
 ("Portable / Camping", ["portable","camping","backpacking","travel","rv ","boat","survival","emergency"]),
 ("Commercial / Industrial", ["commercial","industrial","agriculture","farm","factory","municipal"]),
 ("For Home / Residential", ["for home","home use","residential","household","apartment"]),
 ("Specs / How it Works", ["how does","how it works","work","stages","specs","specification","diagram","manual"]),
 ("Removal (contaminant)", ["remove","removal","that removes","reduces","get rid of"]),
 ("Rental / Lease", ["rent","rental","lease","subscription"]),
 ("Used / Refurbished", ["used","refurbished","second hand","pre owned"]),
 ("Free / Trial", ["free","trial","demo"]),
]

def tag_keyword(kw):
    k=" "+kw.lower()+" "
    for name,trigs in FAMILIES:
        if any(t in k for t in trigs):
            return name
    return "Core / Unmodified"

def detect_property_segments(all_keywords):
    """Return ordered list of segment families present, by total volume."""
    vol=Counter()
    for kw,v,*_ in all_keywords:
        vol[tag_keyword(kw)] += (v or 0)
    # drop the catch-all from the 'detected' headline list but keep for tagging
    ordered=[(n,vol[n]) for n in vol if n!="Core / Unmodified"]
    ordered.sort(key=lambda x:-x[1])
    return ordered

if __name__=="__main__":
    import sys
    split=json.load(open(sys.argv[1]))
    allk=[]
    for c in split:
        allk+=split[c]["generic"]
    seg=detect_property_segments(allk)
    print("Detected segments (by volume):")
    for n,v in seg[:15]: print(f"  {v:>10,} | {n}")
