import json
# AI/AEO block data per cluster.
# Each entry: list of rows = (conversational_query, google_vol_or_blank, ai_overview_bool, cited_sources_str)
# google_vol: real Google volume where known (proxy for AI demand), else "" 
# ai_overview: True if the query triggers a Google AI Overview (live-verified)
# cited: top domains Google's AI Overview cites for that query (live-verified)
A = {}

A["Water Softener"]=[
 ("is a water softener worth it", 5400, True,
  "realtor.com, consumerreports.org, energy.gov, reddit.com, servicelegends.com, aquasana.com"),
 ("what is the downside of a water softener", 1900, True,
  "AI Overview (async) — pull live to capture sources"),
 ("how much does a water softener cost", 8100, True,
  "qualitywatertreatment.com, aquasana.com, culligan.com, lowes.com"),
]

A["Reverse Osmosis"]=[
 ("is reverse osmosis water safe to drink", 2400, True,
  "apecwater.com, watertechnologies.com, epa.gov, reddit.com, bluevua.com"),
 ("what are the disadvantages of reverse osmosis", 1300, True,
  "donovanac.com (Things-to-know), espwaterproducts.com, apecwater.com"),
 ("does reverse osmosis remove pfas", 1000, True,
  "AI Overview (async) — pull live to capture sources"),
]

A["Whole House / POE"]=[
 ("is a whole house water filter worth it", 880, True,
  "aquasana.com, springwellwater.com, expresswater.com, ispringfilter.com, reddit.com"),
 ("how much does a whole house water filtration system cost", 1600, True,
  "AI Overview (async) — pull live to capture sources"),
 ("what does a whole house water filter remove", 720, True,
  "aquasana.com, allfilters.com, ispringfilter.com"),
]

json.dump(A, open("aeo.json","w"))
print("AEO clusters seeded:", len(A))
