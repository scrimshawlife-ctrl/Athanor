import json
from pathlib import Path
import random

OUT_DIR = Path(".")

RELATIONS = {
    "causes": {
        "template": "If {A} causes {B}, and {B} causes {C}, does {A} cause {C}?",
        "domains": {
            "medicine": [("smoking", "inflammation", "cancer"), ("drug A", "lowers BP", "dizziness"), ("vitamin D deficiency", "weak bones", "fractures")],
            "engineering": [("overheating", "metal fatigue", "cracks"), ("vibration", "bearing wear", "misalignment"), ("corrosion", "pipe thinning", "leaks")],
            "biology": [("gene X", "expresses protein Y", "cell division"), ("predator decline", "prey increase", "vegetation loss"), ("pesticide", "kills insects", "crop yield")],
            "law": [("negligence", "breach of duty", "liability"), ("contract breach", "damages", "compensation"), ("statute violation", "penalty", "fine")],
            "everyday": [("rain", "wet roads", "accidents"), ("studying", "better grades", "admission"), ("exercise", "calorie burn", "weight loss")],
        }
    },
    "precedes": {
        "template": "If {A} precedes {B}, and {B} precedes {C}, does {A} precede {C}?",
        "domains": {
            "medicine": [("symptom", "diagnosis", "treatment"), ("infection", "immune response", "recovery"), ("dose", "peak concentration", "effect")],
            "engineering": [("design", "prototype", "production"), ("requirements", "implementation", "testing"), ("planning", "construction", "inspection")],
            "history": [("treaty", "alliance", "war"), ("invention", "adoption", "transformation"), ("protest", "reform", "revolution")],
            "everyday": [("breakfast", "work", "dinner"), ("alarm", "wake up", "leave"), ("planting", "growth", "harvest")],
        }
    },
    "greater_than": {
        "template": "If {A} is greater than {B}, and {B} is greater than {C}, is {A} greater than {C}?",
        "domains": {
            "medicine": [("drug A efficacy", "drug B efficacy", "drug C efficacy"), ("hospital X mortality", "hospital Y mortality", "hospital Z mortality"), ("treatment 1 side effects", "treatment 2 side effects", "treatment 3 side effects")],
            "engineering": [("material X strength", "material Y strength", "material Z strength"), ("algorithm A speed", "algorithm B speed", "algorithm C speed"), ("component X lifespan", "component Y lifespan", "component Z lifespan")],
            "finance": [("stock A return", "stock B return", "stock C return"), ("fund X risk", "fund Y risk", "fund Z risk"), ("bond A yield", "bond B yield", "bond C yield")],
            "everyday": [("Alice height", "Bob height", "Carol height"), ("restaurant X price", "restaurant Y price", "restaurant Z price"), ("task A duration", "task B duration", "task C duration")],
        }
    },
    "enables": {
        "template": "If {A} enables {B}, and {B} enables {C}, does {A} enable {C}?",
        "domains": {
            "medicine": [("diagnosis", "targeted therapy", "recovery"), ("vaccination", "immunity", "disease prevention"), ("screening", "early detection", "better outcome")],
            "engineering": [("sensor data", "control system", "automation"), ("modular design", "rapid prototyping", "faster iteration"), ("standard interface", "interoperability", "system integration")],
            "biology": [("photosynthesis", "glucose production", "plant growth"), ("pollination", "fertilization", "seed production"), ("enzyme", "reaction", "metabolic pathway")],
            "everyday": [("internet", "information access", "learning"), ("savings", "investment", "wealth growth"), ("exercise", "fitness", "health")],
        }
    },
    "requires": {
        "template": "If {A} requires {B}, and {B} requires {C}, does {A} require {C}?",
        "domains": {
            "medicine": [("surgery", "anesthesia", "anesthesiologist"), ("transplant", "donor match", "compatibility testing"), ("dialysis", "vascular access", "surgery")],
            "engineering": [("production", "quality control", "testing equipment"), ("deployment", "staging environment", "CI pipeline"), ("scaling", "load balancer", "monitoring")],
            "law": [("lawsuit", "standing", "injury"), ("contract", "consideration", "mutual assent"), ("appeal", "final judgment", "trial court decision")],
            "everyday": [("driving", "license", "driving test"), ("voting", "registration", "citizenship"), ("travel", "passport", "application")],
        }
    },
}

random.seed(42)
items = []

# All atomic components
all_atomic = []
for rel_name, rel_data in RELATIONS.items():
    for domain, triples in rel_data["domains"].items():
        for triple in triples:
            prompt = rel_data["template"].format(A=triple[0], B=triple[1], C=triple[2])
            all_atomic.append({
                "prompt": prompt,
                "relation": rel_name,
                "domain": domain,
                "entities": triple,
                "expected": "yes",
                "type": "atomic"
            })

# 1. SEEN combinations
for i, item in enumerate(all_atomic):
    if i % 3 == 0:
        items.append({
            "row_id": "seen_" + item["relation"] + "_" + item["domain"] + "_" + "{:03d}".format(i),
            "prompt": item["prompt"],
            "relation": item["relation"],
            "domain": item["domain"],
            "entities": item["entities"],
            "expected": item["expected"],
            "condition": "SEEN",
            "combination": "SEEN",
            "depth": 1,
            "intervention_target": "none"
        })

# 2. UNSEEN_COMBINATIONS: novel entity recombinations
for rel_name, rel_data in RELATIONS.items():
    for domain, triples in rel_data["domains"].items():
        if len(triples) >= 3:
            for i in range(len(triples) - 1):
                t1, t2 = triples[i], triples[i+1]
                new_prompt = rel_data["template"].format(A=t1[0], B=t2[1], C=t1[2])
                items.append({
                    "row_id": "unseen_combo_" + rel_name + "_" + domain + "_" + "{:03d}".format(i),
                    "prompt": new_prompt,
                    "relation": rel_name,
                    "domain": domain,
                    "entities": (t1[0], t2[1], t1[2]),
                    "expected": "yes",
                    "condition": "UNSEEN_COMBINATION",
                    "combination": "UNSEEN",
                    "depth": 1,
                    "intervention_target": "relational"
                })

# 3. SAME_RELATION_DIFFERENT_DOMAINS
for rel_name, rel_data in RELATIONS.items():
    domains = list(rel_data["domains"].keys())
    first_domain = domains[0]
    triples = rel_data["domains"][first_domain]
    for triple in triples[:2]:
        for domain in domains[1:]:
            new_prompt = rel_data["template"].format(A=triple[0], B=triple[1], C=triple[2])
            items.append({
                "row_id": "same_rel_diff_dom_" + rel_name + "_" + domain + "_" + "{:03d}".format(domains.index(domain)),
                "prompt": new_prompt,
                "relation": rel_name,
                "domain": domain,
                "entities": triple,
                "expected": "yes",
                "condition": "SAME_RELATION_DIFFERENT_DOMAIN",
                "combination": "SEEN",
                "depth": 1,
                "intervention_target": "domain"
            })

# 4. SAME_DOMAIN_DIFFERENT_RELATIONS
domain_entity_map = {
    "medicine": [("smoking", "inflammation", "cancer"), ("drug A", "lowers BP", "dizziness")],
    "engineering": [("overheating", "metal fatigue", "cracks"), ("vibration", "bearing wear", "misalignment")],
    "biology": [("gene X", "expresses protein Y", "cell division"), ("predator decline", "prey increase", "vegetation loss")],
    "law": [("negligence", "breach of duty", "liability"), ("contract breach", "damages", "compensation")],
    "everyday": [("rain", "wet roads", "accidents"), ("studying", "better grades", "admission")],
    "finance": [("stock A return", "stock B return", "stock C return"), ("fund X risk", "fund Y risk", "fund Z risk")],
    "history": [("treaty", "alliance", "war"), ("invention", "adoption", "transformation")],
}

for domain, triples in domain_entity_map.items():
    for triple in triples:
        for rel_name in RELATIONS:
            if domain in RELATIONS[rel_name]["domains"]:
                new_prompt = RELATIONS[rel_name]["template"].format(A=triple[0], B=triple[1], C=triple[2])
                items.append({
                    "row_id": "same_dom_diff_rel_" + domain + "_" + rel_name + "_" + "{:03d}".format(triples.index(triple)),
                    "prompt": new_prompt,
                    "relation": rel_name,
                    "domain": domain,
                    "entities": triple,
                    "expected": "yes",
                    "condition": "SAME_DOMAIN_DIFFERENT_RELATION",
                    "combination": "SEEN",
                    "depth": 1,
                    "intervention_target": "relational"
                })

# 5. COUNTERFACTUAL
for rel_name, rel_data in RELATIONS.items():
    domain = list(rel_data["domains"].keys())[0]
    triples = rel_data["domains"][domain][:2]
    for j, triple in enumerate(triples):
        base = rel_data["template"].format(A=triple[0], B=triple[1], C=triple[2])
        cf_prompt = "Suppose the opposite were true: " + base
        items.append({
            "row_id": "counterfactual_" + rel_name + "_" + domain + "_" + "{:03d}".format(j),
            "prompt": cf_prompt,
            "relation": rel_name,
            "domain": domain,
            "entities": triple,
            "expected": "no",
            "condition": "COUNTERFACTUAL",
            "combination": "SEEN",
            "depth": 1,
            "intervention_target": "relational"
        })

# 6. DISTRACTOR
distractors = [
    "Note that the sky appears blue during the day.",
    "Remember that water boils at 100 degrees Celsius.",
    "Consider that the earth orbits the sun.",
    "Keep in mind that mammals are warm-blooded.",
]
for rel_name, rel_data in RELATIONS.items():
    domain = list(rel_data["domains"].keys())[0]
    triples = rel_data["domains"][domain][:2]
    for j, triple in enumerate(triples):
        base = rel_data["template"].format(A=triple[0], B=triple[1], C=triple[2])
        dist = distractors[j % len(distractors)]
        dist_prompt = dist + " " + base
        items.append({
            "row_id": "distractor_" + rel_name + "_" + domain + "_" + "{:03d}".format(j),
            "prompt": dist_prompt,
            "relation": rel_name,
            "domain": domain,
            "entities": triple,
            "expected": "yes",
            "condition": "DISTRACTOR",
            "combination": "SEEN",
            "depth": 1,
            "intervention_target": "distractor"
        })

# 7. DEPTH
for rel_name, rel_data in RELATIONS.items():
    domain = list(rel_data["domains"].keys())[0]
    triples = rel_data["domains"][domain]
    if len(triples) >= 4:
        # 2-hop
        prompt_2hop = rel_data["template"].format(A=triples[0][0], B=triples[0][1], C=triples[0][2])
        items.append({
            "row_id": "depth2_" + rel_name + "_" + domain + "_001",
            "prompt": prompt_2hop,
            "relation": rel_name,
            "domain": domain,
            "entities": triples[0],
            "expected": "yes",
            "condition": "DEPTH",
            "combination": "SEEN",
            "depth": 2,
            "intervention_target": "relational"
        })
        # 3-hop
        prompt_3hop = "If " + triples[0][0] + " causes " + triples[0][1] + ", " + triples[0][1] + " causes " + triples[0][2] + ", and " + triples[0][2] + " causes " + triples[1][0] + ", does " + triples[0][0] + " cause " + triples[1][0] + "?"
        items.append({
            "row_id": "depth3_" + rel_name + "_" + domain + "_001",
            "prompt": prompt_3hop,
            "relation": rel_name,
            "domain": domain,
            "entities": (triples[0][0], triples[0][1], triples[1][0]),
            "expected": "yes",
            "condition": "DEPTH",
            "combination": "SEEN",
            "depth": 3,
            "intervention_target": "relational"
        })
        # 4-hop
        if len(triples) >= 3:
            prompt_4hop = "If " + triples[0][0] + " causes " + triples[0][1] + ", " + triples[0][1] + " causes " + triples[0][2] + ", " + triples[0][2] + " causes " + triples[1][0] + ", and " + triples[1][0] + " causes " + triples[1][1] + ", does " + triples[0][0] + " cause " + triples[1][1] + "?"
            items.append({
                "row_id": "depth4_" + rel_name + "_" + domain + "_001",
                "prompt": prompt_4hop,
                "relation": rel_name,
                "domain": domain,
                "entities": (triples[0][0], triples[0][1], triples[1][1]),
                "expected": "yes",
                "condition": "DEPTH",
                "combination": "SEEN",
                "depth": 4,
                "intervention_target": "relational"
            })

# Write evaluation surface
with open(OUT_DIR / "causality_eval.jsonl", "w") as f:
    for item in items:
        f.write(json.dumps(item) + "\n")

# Write metadata
with open(OUT_DIR / "causality_metadata.json", "w") as f:
    metadata = {
        "total_items": len(items),
        "conditions": list(set(item["condition"] for item in items)),
        "relations": list(RELATIONS.keys()),
        "domains": list(set(item["domain"] for item in items)),
        "conditions_count": {}
    }
    from collections import Counter
    cond_counts = Counter(item["condition"] for item in items)
    metadata["conditions_count"] = dict(cond_counts)
    json.dump(metadata, f, indent=2)

print("Total evaluation items:", len(items))
print("Atomic components:", len(all_atomic))
print("Conditions:", list(set(item["condition"] for item in items)))
print("Relations:", list(RELATIONS.keys()))
print("Domains:", list(set(item["domain"] for item in items)))
from collections import Counter
cond_counts = Counter(item["condition"] for item in items)
for cond, count in cond_counts.items():
    print("  " + cond + ":", count)