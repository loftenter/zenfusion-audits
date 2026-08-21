import json
H = json.load(open("paa_deep.json"))  # Water Softener, Reverse Osmosis (live, merged)

# Whole House — merged across 'whole house water filter' + 'whole house water filtration system'
H["Whole House / POE"]={
 "paa": list(dict.fromkeys([
  "Is it worth getting a whole house water filter?","How much should a whole house water filtration system cost?",
  "What is the best water filter system for a whole house?","What are the disadvantages of a whole house water filter?",
  "What is the lifespan of a whole house water filter?","How much does a Culligan whole house water filtration system cost?",
  "How much does a whole house water filtration system cost?","What is the best whole house water filtration system for home?",
  "Is it worth getting a whole house water filtration system?","Which is better, Kinetico or Culligan?",
  "How much should a whole house filtration system cost?","Why not drink reverse osmosis water?",
 ])),
 "things":["What is the lifespan of a whole house water filter?","How does a whole house water filter work?",
           "What are the different types of whole house water filters?",
           "What contaminants does a whole house water filtration system remove?",
           "How to maintain a whole house water filtration system?"],
 "related":["Best whole house water filter","Whole house water filter with softener","Whole house water filter replacement",
            "Whole house water filter for city water","Whole house water filter cartridge","Whole house water filter for well water",
            "Best whole house sediment filter","Best whole house water filter for lead","NSF certified whole house water filter",
            "Cheapest whole house water filtration system","DIY whole house water filtration system","Whole house water filtration system reviews"],
 "live":True}

# Water Filter head (from earlier live pull)
H["Water Filter (head)"]={
 "paa": list(dict.fromkeys([
  "What is the best water filter for drinking?","What is the best type of water filter to get?",
  "Can povidone iodine be used to purify water?","What is a life straw?",
 ])),
 "things":["How to choose a water filter?","How long do water filters last?",
           "What are the benefits of using a water filter?","What are the different types of water filters?",
           "How do water filters work?"],
 "related":["Water filter for drinking","Water filter home","Water filter for sink","Water filter science",
            "Water filter refrigerator","Water filter shower","Water filter countertop","Water filter PUR"],
 "live":True}

# ---- Expanded DERIVED sets for remaining clusters (richer pattern library) ----
def d(paa, things, related): return {"paa":paa,"things":things,"related":related,"derived":True}

H["Home / Residential"]=d(
 ["What is the best water filtration system for a home?","Is a home water filtration system worth it?",
  "How much does a home water filtration system cost?","What does a home water filter remove?",
  "What is the best home water filter for the money?","Do home water filters really work?",
  "How long do home water filtration systems last?","Should I filter my whole home or just drinking water?"],
 ["How home water filtration works","Types of home water filtration systems","Home water filter maintenance",
  "Home water filter lifespan","Choosing a home water filter"],
 ["Home water filtration system reviews","Home water filter cost","Best home water filtration system 2026",
  "Home water filter installation","Home water filtration system for well water","Whole home water filter"])

H["Water Filtration System"]=d(
 ["What is the best water filtration system?","Is a water filtration system worth it?",
  "How much does a water filtration system cost?","What is the healthiest water filtration system?",
  "What does a water filtration system remove?","How long do water filtration systems last?",
  "What is the best water filtration system for the money?","Whole house vs under sink filtration?"],
 ["How water filtration systems work","Types of water filtration systems","Water filtration system maintenance",
  "Water filtration system lifespan","Contaminants removed by filtration systems"],
 ["Best water filtration system","Water filtration system cost","Water filtration system for home",
  "Water filtration system reviews","Water filtration system for well water","NSF certified water filtration system"])

H["Water Filter System"]=d(
 ["What is the best water filter system?","How much does a water filter system cost?",
  "Are water filter systems worth it?","What does a water filter system remove?",
  "What is the best water filter system for home use?","How long does a water filter system last?",
  "Which water filter system is healthiest?"],
 ["How water filter systems work","Types of water filter systems","Water filter system maintenance",
  "Water filter system lifespan"],
 ["Best water filter system","Water filter system cost","Water filter system for home","Water filter system reviews",
  "Water filter system for well water","Under sink water filter system"])

H["House Water Filter"]=d(
 ["Is a house water filter worth it?","What is the best house water filter?","How much is a house water filter?",
  "What does a house water filter remove?","How long does a house water filter last?","Are house water filters worth the money?"],
 ["How a house water filter works","Types of house water filters","House water filter lifespan","House water filter maintenance"],
 ["Best house water filter","House water filter cost","House water filter system","House water filter installation",
  "Whole house water filter","House water filter replacement"])

H["Well Water"]=d(
 ["What is the best filtration system for well water?","How do I filter my well water?",
  "What should I filter out of well water?","Is well water safe to drink without filtering?",
  "How much does a well water filtration system cost?","Why does my well water smell like rotten eggs?",
  "Do I need a water softener or filter for well water?","How often should well water be tested?",
  "What removes iron from well water?","Is well water better than city water?"],
 ["How well water filtration works","Types of well water filters","Well water testing","Iron & sulfur in well water",
  "Well water treatment stages"],
 ["Best well water filtration system","Well water filter cost","Well water filter for iron",
  "Well water filtration system reviews","Well water sediment filter","Well water filter and softener combo",
  "Well water filtration system for rotten egg smell"])

H["Under-Sink"]=d(
 ["What is the best under sink water filter?","Are under sink water filters worth it?",
  "How much does an under sink water filter cost?","How long do under sink water filters last?",
  "Do under sink water filters need plumbing?","Under sink filter vs reverse osmosis?",
  "What does an under sink water filter remove?","Can I install an under sink water filter myself?"],
 ["How under sink water filters work","Under sink filter vs RO","Under sink filter installation",
  "Under sink filter maintenance"],
 ["Best under sink water filter","Under sink water filter system","Under sink water filter installation",
  "Under counter water filter","Under sink water filter reviews","Under sink reverse osmosis"])

H["Countertop & Pitcher"]=d(
 ["What is the best countertop water filter?","Are water filter pitchers worth it?",
  "What is the best water filter pitcher?","Do countertop water filters remove fluoride?",
  "Which water filter pitcher removes the most contaminants?","Is a Brita or PUR filter better?",
  "Do water filter pitchers remove PFAS?","How often should you change a water filter pitcher?","Is Berkey worth the money?"],
 ["How countertop filters work","Pitcher vs countertop vs faucet","Countertop filter maintenance","Pitcher filter lifespan"],
 ["Best countertop water filter","Best water filter pitcher","Countertop reverse osmosis","Water filter pitcher reviews",
  "Berkey water filter","ZeroWater vs Brita"])

H["Faucet & Inline"]=d(
 ["What is the best faucet water filter?","Do faucet water filters work?",
  "How long do faucet water filters last?","Are faucet water filters worth it?",
  "Do faucet filters remove fluoride?","Which is better, faucet or pitcher filter?","How do you install a faucet water filter?"],
 ["How faucet filters work","Faucet filter installation","Faucet filter vs pitcher","Faucet filter lifespan"],
 ["Best faucet water filter","Faucet water filter reviews","Faucet mount water filter","Inline water filter",
  "PUR faucet filter","Brita faucet filter"])

H["Refrigerator/Fridge"]=d(
 ["How often should you change a refrigerator water filter?","Do refrigerator water filters really work?",
  "Are generic refrigerator water filters safe?","What happens if you don't change your fridge water filter?",
  "Do refrigerator water filters remove fluoride?","Are aftermarket fridge filters as good as OEM?",
  "Why are refrigerator water filters so expensive?"],
 ["How refrigerator filters work","Refrigerator filter replacement","Refrigerator filter compatibility","Fridge filter lifespan"],
 ["Refrigerator water filter replacement","Refrigerator water filter by model","Generic refrigerator water filter",
  "Fridge water filter","Everydrop water filter","Refrigerator water filter near me"])

H["Water Purifier"]=d(
 ["What is the difference between a water filter and a water purifier?","What is the best water purifier?",
  "Is a water purifier worth it?","Do water purifiers remove bacteria?",
  "What is the best water purifier for home?","Which water purifier is best for health?",
  "Do I need a water purifier if I have city water?","What does a water purifier remove that a filter doesn't?"],
 ["How water purifiers work","Water purifier vs filter","Types of water purifiers","Water purifier maintenance"],
 ["Best water purifier","Water purifier for home","Water purifier vs filter","Water purifier system",
  "Best water purifier for home use","Water purification system"])

H["PFAS / Lead"]=d(
 ["What water filter removes PFAS?","Does reverse osmosis remove PFAS?",
  "What is the best water filter for lead?","Do Brita filters remove PFAS?",
  "What is the best filter to remove forever chemicals?","Does boiling water remove PFAS?",
  "How do I know if my water has PFAS?","Does a refrigerator filter remove lead?","What removes lead from drinking water?"],
 ["How to remove PFAS from water","How to remove lead from water","NSF certification for PFAS/lead","Testing for PFAS and lead"],
 ["Best PFAS water filter","Water filter that removes lead","PFAS filter for home","Does RO remove PFAS",
  "Best water filter for forever chemicals","Lead water filter"])

H["Fluoride Filter"]=d(
 ["What water filter removes fluoride?","Does reverse osmosis remove fluoride?",
  "Do Brita filters remove fluoride?","Is fluoride in water bad for you?",
  "How do you remove fluoride from drinking water?","Does boiling water remove fluoride?",
  "Does a whole house filter remove fluoride?","What is the best fluoride water filter for home?"],
 ["How to remove fluoride from water","Fluoride removal methods","RO & fluoride","Activated alumina for fluoride"],
 ["Best fluoride water filter","Water filter that removes fluoride","Fluoride removal water filter","Does RO remove fluoride",
  "Fluoride filter for whole house","Berkey fluoride filter"])

H["Iron Filter"]=d(
 ["What is the best iron filter for well water?","How do I remove iron from well water?",
  "What causes iron in well water?","Does a water softener remove iron?",
  "How much does an iron filter cost?","What is the best way to remove iron from water?",
  "Will an iron filter remove rotten egg smell?","How long do iron filters last?"],
 ["How iron filters work","Types of iron filters","Iron filter maintenance","Iron vs sulfur removal","Air injection iron removal"],
 ["Best iron filter for well water","Whole house iron filter","Air injection iron filter","Iron removal filter",
  "Iron filter cost","Iron and manganese filter"])

H["Carbon / Media"]=d(
 ["What does a carbon water filter remove?","How long do carbon water filters last?",
  "Is activated carbon good for water filtration?","What is the difference between GAC and carbon block?",
  "Does a carbon filter remove fluoride?","Does carbon filter remove bacteria?","Is catalytic carbon better than activated carbon?"],
 ["How activated carbon works","GAC vs carbon block vs catalytic","Carbon filter lifespan","What carbon filters remove"],
 ["Activated carbon water filter","Carbon block water filter","Catalytic carbon filter","Whole house carbon filter",
  "Coconut shell carbon filter","Carbon water filter replacement"])

H["Chlorine / Chloramine"]=d(
 ["How do you remove chlorine from water?","What filter removes chloramine?",
  "Does a carbon filter remove chlorine?","Is chlorine in tap water harmful?",
  "What is the difference between chlorine and chloramine?","Does boiling water remove chlorine?",
  "Does reverse osmosis remove chlorine?","How do I remove chloramine from tap water?"],
 ["How to remove chlorine","Chlorine vs chloramine removal","Dechlorination methods","Catalytic carbon for chloramine"],
 ["Best chlorine water filter","Whole house chlorine filter","Water filter that removes chlorine","Dechlorinator",
  "Chloramine water filter","Shower filter for chlorine"])

H["Sediment & Specialty Well"]=d(
 ["What does a sediment filter remove?","What micron sediment filter do I need?",
  "How often should I change a sediment filter?","Do I need a sediment filter for well water?",
  "What is the best sediment filter for well water?","Spin-down vs cartridge sediment filter?",
  "Does a sediment filter remove iron?","What removes tannins from well water?"],
 ["How sediment filters work","Micron ratings explained","Spin-down vs cartridge sediment filters","Tannin removal"],
 ["Best sediment filter for well water","Whole house sediment filter","Spin down sediment filter","Sediment filter micron",
  "Tannin filter for well water","Sediment pre-filter"])

H["UV / Disinfection"]=d(
 ["Do UV water purifiers work?","Is a UV water filter worth it?",
  "Does UV light kill bacteria in water?","How often do you replace a UV water filter bulb?",
  "Do I need a UV filter for well water?","Does a UV filter remove viruses?",
  "Can you drink water right after UV treatment?","How much does a UV water purifier cost?"],
 ["How UV purification works","When you need UV","UV bulb maintenance","UV vs chemical disinfection"],
 ["Best UV water purifier","UV water filter for well water","Whole house UV water filter","UV water purification system",
  "UV filter for bacteria","UV water sterilizer"])

H["Alkaline / Ionizer / Hydrogen"]=d(
 ["Is alkaline water actually good for you?","Do water ionizers really work?",
  "What is hydrogen water and is it healthy?","What is the best water ionizer?",
  "Is alkaline water bad for your kidneys?","Does alkaline water have side effects?",
  "What is the difference between alkaline and hydrogen water?","Is a hydrogen water machine worth it?","Are water ionizers a scam?"],
 ["How ionizers work","Alkaline vs hydrogen vs ionized","Ionizer pH levels","Hydrogen water benefits"],
 ["Best water ionizer","Hydrogen water machine","Alkaline water filter","Water ionizer reviews",
  "Kangen water machine","Alkaline water pitcher"])

H["Water Distiller"]=d(
 ["Is distilled water safe to drink?","What is the best water distiller?",
  "Is distilled water better than filtered water?","How long does a water distiller take?",
  "Is it healthy to drink distilled water daily?","Distiller vs reverse osmosis: which is better?",
  "Does a water distiller remove fluoride?","How much electricity does a water distiller use?"],
 ["How water distillers work","Distiller vs RO","Distiller maintenance","What distillation removes"],
 ["Best water distiller","Countertop water distiller","Water distiller vs reverse osmosis","Water distiller reviews",
  "Distilled water for drinking","Megahome water distiller"])

H["Portable / Camping / Survival Purifier"]=d(
 ["What is the best portable water filter for backpacking?","Do portable water filters remove viruses?",
  "Sawyer vs Katadyn: which is better?","How do you purify water in an emergency?",
  "What is the best survival water filter?","Do water purification tablets work?",
  "How long do portable water filters last?","What is the difference between a filter and a purifier for camping?"],
 ["How portable filters work","Filter vs purifier for travel","Water purification tablets","Backcountry water safety"],
 ["Best portable water filter","Backpacking water filter","Survival water filter","Water purification tablets",
  "Sawyer water filter","LifeStraw vs Sawyer"])

H["Best / Reviews / Compare"]=d(
 ["What is the best water filtration system?","What water filter do experts recommend?",
  "What is the best water filter brand?","What is the most effective water filter?",
  "What water filter does Consumer Reports recommend?","Which water filter removes the most contaminants?",
  "What is the best value water filter?","Is Berkey or reverse osmosis better?"],
 ["How to compare water filters","What to look for in a water filter","NSF certifications explained","Filter testing methodology"],
 ["Best water filter Consumer Reports","Best water filter brand","Best whole house water filter","Best water filter 2026",
  "Best water filter Reddit","Most effective water filter"])

H = {k:v for k,v in H.items() if v}
json.dump(H, open("paa_all.json","w"))
print("Total clusters:", len(H))
for k in H:
    n=len(H[k]["paa"])+len(H[k]["things"])+len(H[k]["related"])
    print(f"  {'LIVE ' if H[k].get('live') else 'deriv'} | {n:>3} total | {k}")
