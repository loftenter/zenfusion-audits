# Industry-agnostic topical-map generator.
# For a core keyword: derive ~11 sub-clusters, ~10 long-tails each, ~10 click-worthy titles each.
import re, random

# Sub-cluster archetypes (intent-tagged) — generic across industries.
SUBCLUSTERS = [
 ("{C} Benefits", "Informational", ["{C} Benefits","Advantages of {C}","Why Use {C}","{C} for Better Health",
   "{C} vs Going Without","Top Reasons to Get {C}","Hidden Benefits of {C}","{C} Pros and Cons",
   "What {C} Does for You","Long-Term Benefits of {C}"]),
 ("How {C} Works", "Informational", ["How {C} Works","{C} Explained","The Science Behind {C}","{C} Process Step by Step",
   "What Happens Inside {C}","{C} Technology Explained","How {C} Removes Contaminants","{C} Stages Explained",
   "Understanding {C}","{C} Diagram and Breakdown"]),
 ("Types of {C}", "Informational", ["Types of {C}","{C} Options Compared","Which {C} Type Is Right for You",
   "{C} Buying Categories","Different Kinds of {C}","{C} Styles and Configurations","Choosing a {C} Type",
   "{C} Type Comparison","Popular {C} Variations","{C} Tiers Explained"]),
 ("Best {C} (Reviews)", "Commercial", ["Best {C} ({Y})","Top {C} Reviewed","{C} Buyer's Guide","Best {C} for the Money",
   "{C} Comparison Chart","Highest-Rated {C}","{C} Reviews and Ratings","Best {C} for Home Use",
   "{C} Picks by Experts","Most Popular {C} This Year"]),
 ("{C} Cost & Pricing", "Commercial", ["{C} Cost ({Y})","How Much Does {C} Cost","{C} Price Guide","Is {C} Worth the Money",
   "{C} Cost vs Benefits","Cheapest {C} Options","{C} Pricing Explained","Budget {C} That Works",
   "{C} Cost of Ownership","What You'll Really Pay for {C}"]),
 ("{C} Installation", "Transactional", ["How to Install {C}","{C} Installation Guide","DIY {C} Installation",
   "{C} Setup Step by Step","Professional vs DIY {C} Install","{C} Installation Cost","{C} Install Mistakes to Avoid",
   "{C} Installation Checklist","Installing {C} Yourself","{C} Setup Made Simple"]),
 ("{C} Maintenance", "Informational", ["{C} Maintenance Guide","How to Maintain {C}","{C} Upkeep Tips",
   "{C} Cleaning and Care","{C} Replacement Schedule","Extend {C} Lifespan","{C} Troubleshooting",
   "Common {C} Problems","{C} Care Checklist","Keep Your {C} Running Longer"]),
 ("{C} vs Alternatives", "Commercial", ["{C} vs Alternatives","{C} or the Alternative: Which Wins","{C} Compared to Other Options",
   "Is {C} Better Than the Rest","{C} Head-to-Head Comparison","When to Choose {C} Over Alternatives",
   "{C} vs the Competition","Switching to {C}: Worth It","{C} Showdown","Why {C} Beats the Alternatives"]),
 ("{C} for Specific Needs", "Informational", ["{C} for Families","{C} for Small Spaces","{C} for Renters",
   "{C} for Large Homes","{C} for Beginners","Best {C} for Your Situation","{C} for Special Cases",
   "Choosing {C} for Your Needs","{C} That Fits Your Lifestyle","Right-Sizing Your {C}"]),
 ("{C} Buying Guide", "Commercial", ["{C} Buying Guide","What to Look for in {C}","{C} Features That Matter",
   "Before You Buy {C}","{C} Shopping Checklist","Avoid These {C} Buying Mistakes","Smart {C} Shopping Tips",
   "{C} Specs Explained","How to Choose {C}","{C} Buyer Beware"]),
 ("{C} Questions Answered", "Informational", ["{C} FAQ","Common {C} Questions","{C} Myths Debunked",
   "Everything About {C}","{C} Questions You Were Afraid to Ask","Truth About {C}","{C} Facts vs Fiction",
   "{C} Answers for Beginners","Your {C} Questions Solved","{C} Explained Simply"]),
]

# Click-worthy title transformation templates. {T}=base title, {C}=core, {Y}=year
HOOKS = [
 "{T}", "{T} (You'll Wish You Knew Sooner)", "The Truth About {Tlow}",
 "{T} — What Nobody Tells You", "Stop Wasting Money: {Tlow}",
 "{T} in {Y}", "Why {Clow} Could Be the Best Decision You Make",
 "{T}: A No-BS Guide", "Everyone's Asking About {Clow} — Here's the Answer",
 "{T} (Backed by Real Data)", "Before You Buy: {Tlow}",
 "{T} That Actually Work", "The Surprising Truth About {Clow}",
 "{T} — Don't Get Ripped Off", "Is {Clow} a Scam or a Game-Changer?",
 "{Number} Things to Know About {Clow}", "{T}, Explained in Plain English",
 "What the Experts Won't Tell You About {Clow}", "{T} (2026 Update)",
 "The Only {Clow} Guide You'll Ever Need",
]
NUMS=["7","9","5","11","13","6","8","10","12"]

def titlecase_keep(s): return s

def click_titles(base, core, n=10, year="2026"):
    out=[]
    seeds=list(HOOKS)
    random.shuffle(seeds)
    used=set()
    # keep core readable: "a Fluoride Filter" reads better than "fluoride filter" mid-sentence
    core_phrase = core if core[0].isupper() else core
    for hook in seeds:
        t=(hook.replace("{T}",base)
               .replace("{Tlow}",base)
               .replace("{Clow}",core_phrase)
               .replace("{C}",core)
               .replace("{Y}",year)
               .replace("{Number}",random.choice(NUMS)))
        # tidy: collapse accidental double spaces, fix " a Fluoride" style
        t=re.sub(r"\s+"," ",t).strip()
        if t not in used:
            used.add(t); out.append(t)
        if len(out)>=n: break
    # backfill if needed
    i=0
    while len(out)<n:
        out.append(f"{base} ({year}) #{i+1}"); i+=1
    return out[:n]

def build_topical_map(core, n_sub=11, n_lt=10, n_titles=10):
    """Return list of (subcluster, long_tail, intent, title)."""
    rows=[]
    subs = SUBCLUSTERS[:n_sub]
    for sub_tmpl, intent, lt_tmpls in subs:
        sub = sub_tmpl.replace("{C}", core)
        lts = [t.replace("{C}",core).replace("{Y}","2026") for t in lt_tmpls[:n_lt]]
        for lt in lts:
            titles = click_titles(lt, core, n=n_titles)
            for tt in titles:
                rows.append((sub, lt, intent, tt))
    return rows

if __name__=="__main__":
    rows=build_topical_map("Fluoride Filter")
    print("rows:",len(rows))
    for r in rows[:12]: print("  ",r[0],"|",r[1],"|",r[2],"|",r[3])
