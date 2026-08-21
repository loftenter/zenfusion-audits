import json
# Deep PAA harvest — merging multiple keyword-variant PAA trees per cluster.
# Each cluster: union of all questions seen across variant SERP pulls (live).
H = {}

H["Water Softener"] = {
 "paa": list(dict.fromkeys([
  # variant: water softener
  "What is the downside of a water softener?","Is a water softener worth having?",
  "What is the best water softener for calcium?","What city in the US has the hardest water?",
  "Why are states banning water softeners?","What's the average lifespan of a water softener?",
  "How big of a water softener do I need for a family of 5?","How much does Home Depot charge to install a water softener?",
  "What's better than a water softener?","What city has the purest water in the US?","What kills parasites in water?",
  # variant: water softener cost
  "What is the average cost of a water softener?","Do I need a plumber to install a water softener?",
  "Is a water softener worth the money?","Can I write off a water softener on my taxes?",
  "How much does Lowe's charge to install a water softener?",
  "How much does it cost for a plumber to install a water softener system?",
 ])),
 "things":["How does water softening work?","How to maintain a water softener?",
           "What are the different methods of water softening?","What are the benefits of water softening?"],
 "related":["Water softener salt","Water softener for shower","Water softener Lowe's","Water softener installation",
            "Water softener menards","Water softener Reddit","Water softener tank","Water softener near me",
            "Water softener system Costco","How much does a water softener cost per month","Water softener cost installed",
            "Whole house water softener and filtration system","Costco water softener system cost"],
 "live":True}

json.dump(H, open("paa_deep.json","w"))
print("Water Softener PAA (deep):", len(H["Water Softener"]["paa"]), "unique questions")

H["Reverse Osmosis"]={
 "paa": list(dict.fromkeys([
  "Is it healthy to drink reverse osmosis water?","What is the downside of reverse osmosis?",
  "What are the downsides of reverse osmosis water?","What is reverse osmosis and how does it work?",
  "Does reverse osmosis get rid of nitrates?","Is RO water hard on the kidneys?",
  "What is the #1 healthiest water to drink?","Is there a downside to drinking reverse osmosis water?",
  "What is a major problem with reverse osmosis?","How to flush nitrates out of your body?",
 ])),
 "things":["How does reverse osmosis work?","What are the disadvantages of reverse osmosis?",
           "What are the benefits of reverse osmosis?","What are the different types of reverse osmosis systems?",
           "What is the history of reverse osmosis?"],
 "related":["Reverse osmosis system for home","Best reverse osmosis system","Reverse osmosis system cost",
            "Reverse osmosis system under sink","Reverse osmosis system Reddit","Waterdrop reverse osmosis system",
            "Reverse osmosis system countertop","Reverse osmosis system Amazon"],
 "live":True}
json.dump(H, open("paa_deep.json","w"))
print("clusters now:",len(H))
