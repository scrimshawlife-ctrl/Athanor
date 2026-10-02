import json
from pathlib import Path
import random

OUT_DIR = Path(".")
random.seed(42)

# Training relations (5 families, same as TRANSFER-001)
RELATIONS = {
    "causal_chain": {
        "template": "If {A} causes {B}, and {B} causes {C}, does {A} cause {C}?",
        "domains": {
            "medicine": [("smoking", "inflammation", "cancer"), ("drug A", "lowers BP", "dizziness"), ("vitamin D deficiency", "weak bones", "fractures")],
            "engineering": [("overheating", "metal fatigue", "cracks"), ("vibration", "bearing wear", "misalignment"), ("corrosion", "pipe thinning", "leaks")],
            "biology": [("gene X", "expresses protein Y", "cell division"), ("predator decline", "prey increase", "vegetation loss"), ("pesticide", "kills insects", "crop yield")],
            "law": [("negligence", "breach of duty", "liability"), ("contract breach", "damages", "compensation"), ("statute violation", "penalty", "fine")],
            "everyday": [("rain", "wet roads", "accidents"), ("studying", "better grades", "admission"), ("exercise", "calorie burn", "weight loss")],
        },
        "held_out": "finance"
    },
    "transitive_ordering": {
        "template": "If {A} is greater than {B}, and {B} is greater than {C}, is {A} greater than {C}?",
        "domains": {
            "medicine": [("drug A efficacy", "drug B efficacy", "drug C efficacy"), ("hospital X mortality", "hospital Y mortality", "hospital Z mortality"), ("treatment 1 side effects", "treatment 2 side effects", "treatment 3 side effects")],
            "engineering": [("material X strength", "material Y strength", "material Z strength"), ("algorithm A speed", "algorithm B speed", "algorithm C speed"), ("component X lifespan", "component Y lifespan", "component Z lifespan")],
            "finance": [("stock A return", "stock B return", "stock C return"), ("fund X risk", "fund Y risk", "fund Z risk"), ("bond A yield", "bond B yield", "bond C yield")],
            "everyday": [("Alice height", "Bob height", "Carol height"), ("restaurant X price", "restaurant Y price", "restaurant Z price"), ("task A duration", "task B duration", "task C duration")],
        },
        "held_out": "biology"
    },
    "counterfactual_override": {
        "template": "Suppose {A} would normally cause {B}. But if we intervene to prevent {B}, what happens to the effect of {A} on {C}?",
        "domains": {
            "medicine": [("antibiotics", "bacterial death", "infection"), ("vaccines", "immunity", "disease"), ("surgery", "tumor removal", "cancer")],
            "engineering": [("water cooling", "temperature reduction", "overheating"), ("steel reinforcement", "strength increase", "structural failure"), ("insulation", "heat retention", "energy loss")],
            "biology": [("predator introduction", "prey decrease", "ecosystem"), ("fertilizer", "plant growth", "crop yield"), ("pesticide", "insect death", "pollination")],
            "law": [("contract signing", "obligation", "performance"), ("evidence admission", "conviction", "trial"), ("statute enactment", "regulation", "compliance")],
        },
        "held_out": "everyday"
    },
    "compositional_reasoning": {
        "template": "If {A} {op1} {B}, and {B} {op2} {C}, and {C} {op3} {D}, what is the relation between {A} and {D}?",
        "domains": {
            "medicine": [("treatment A", "improves", "symptom B", "improves", "condition C", "improves", "outcome D"),
                       ("drug X", "lowers", "pressure Y", "lowers", "risk Z", "lowers", "mortality W"),
                       ("screening", "detects", "stage 1", "allows", "early treatment", "improves", "survival")],
            "biology": [("species A", "eats", "species B", "eats", "species C", "eats", "species D"),
                      ("gene X", "activates", "gene Y", "activates", "gene Z", "activates", "pathway W"),
                      ("nutrient A", "enables", "process B", "enables", "function C", "enables", "growth D")],
            "law": [("statute A", "amends", "statute B", "amends", "statute C", "amends", "statute D"),
                  ("precedent A", "cites", "precedent B", "cites", "precedent C", "cites", "precedent D"),
                  ("court A", "overrules", "court B", "overrules", "court C", "overrules", "court D")],
            "everyday": [("saving money", "enables", "investment", "enables", "wealth", "enables", "freedom"),
                       ("exercise", "improves", "fitness", "improves", "health", "improves", "longevity"),
                       ("learning", "enables", "skill", "enables", "job", "enables", "income")],
        },
        "held_out": "engineering"
    },
    "analogical_mapping": {
        "template": "In domain 1, {A1} is to {B1} as in domain 2, {A2} is to what?",
        "domains": {
            "engineering": [("resistor", "current", "valve", "flow"), ("capacitor", "charge", "tank", "water"), ("diode", "one-way current", "check valve", "one-way flow")],
            "biology": [("heart", "blood", "pump", "water"), ("brain", "signals", "computer", "data"), ("immune system", "pathogens", "antivirus", "malware")],
            "law": [("judge", "interprets law", "referee", "enforces rules"), ("precedent", "guides cases", "standard", "guides implementation"), ("contract", "binds parties", "license", "binds users")],
            "everyday": [("key", "opens lock", "password", "opens account"), ("map", "guides traveler", "recipe", "guides cook"), ("foundation", "supports building", "premise", "supports argument")],
        },
        "held_out": "medicine"
    },
}

# Novel relations for testing (NOT in training)
NOVEL_RELATIONS = {
    "precedes": {
        "template": "If {A} precedes {B}, and {B} precedes {C}, does {A} precede {C}?",
        "domains": {
            "medicine": [("symptom", "diagnosis", "treatment"), ("infection", "immune response", "recovery"), ("dose", "peak concentration", "effect")],
            "engineering": [("design", "prototype", "production"), ("requirements", "implementation", "testing"), ("planning", "construction", "inspection")],
            "history": [("treaty", "alliance", "war"), ("invention", "adoption", "transformation"), ("protest", "reform", "revolution")],
            "everyday": [("breakfast", "work", "dinner"), ("alarm", "wake up", "leave"), ("planting", "growth", "harvest")],
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

# Build training examples
def make_example(prompt, relation, domain, variant, expected="yes"):
    return {"prompt": prompt, "relation": relation, "domain": domain, "variant": variant, "expected": expected}

# CONTROL: Ordinary domain-diverse examples (random sampling across all relations/domains)
control_examples = []
for rel_name, rel_data in RELATIONS.items():
    for domain, triples in rel_data["domains"].items():
        for triple in triples:
            # Base
            if rel_name == "compositional_reasoning":
                prompt = rel_data["template"].format(A=triple[0], op1=triple[1], B=triple[2], op2=triple[3], C=triple[4], op3=triple[5], D=triple[6])
            elif rel_name == "analogical_mapping":
                prompt = rel_data["template"].format(A1=triple[0], B1=triple[1], A2=triple[2])
            else:
                prompt = rel_data["template"].format(A=triple[0], B=triple[1], C=triple[2])
            control_examples.append(make_example(prompt, rel_name, domain, "base"))
            # Paraphrase
            for p in ["Rephrased: " + prompt, "In different words: " + prompt]:
                control_examples.append(make_example(p, rel_name, domain, "paraphrase"))
            # Counterfactual
            control_examples.append(make_example("What if the opposite were true? " + prompt, rel_name, domain, "counterfactual"))
            # Compositional
            control_examples.append(make_example("Building on this: " + prompt + " What is the next step?", rel_name, domain, "compositional"))
            # Distractor
            for d in ["Irrelevant fact: The sky is blue. " + prompt, "Distractor: Bananas are curved. " + prompt]:
                control_examples.append(make_example(d, rel_name, domain, "distractor"))
            # Hard negative
            control_examples.append(make_example("Incorrect premise: The reverse is true. " + prompt, rel_name, domain, "hard_negative"))

random.shuffle(control_examples)

# STRUCTURAL: Same relations, matched across domains (same total count)
structural_examples = []
for rel_name, rel_data in RELATIONS.items():
    domains = list(rel_data["domains"].keys())
    for domain in domains:
        triples = rel_data["domains"][domain]
        for triple in triples:
            if rel_name == "compositional_reasoning":
                prompt = rel_data["template"].format(A=triple[0], op1=triple[1], B=triple[2], op2=triple[3], C=triple[4], op3=triple[5], D=triple[6])
            elif rel_name == "analogical_mapping":
                prompt = rel_data["template"].format(A1=triple[0], B1=triple[1], A2=triple[2])
            else:
                prompt = rel_data["template"].format(A=triple[0], B=triple[1], C=triple[2])
            structural_examples.append(make_example(prompt, rel_name, domain, "base"))
            for p in ["Rephrased: " + prompt, "In different words: " + prompt]:
                structural_examples.append(make_example(p, rel_name, domain, "paraphrase"))
            structural_examples.append(make_example("What if the opposite were true? " + prompt, rel_name, domain, "counterfactual"))
            structural_examples.append(make_example("Building on this: " + prompt + " What is the next step?", rel_name, domain, "compositional"))
            for d in ["Irrelevant fact: The sky is blue. " + prompt, "Distractor: Bananas are curved. " + prompt]:
                structural_examples.append(make_example(d, rel_name, domain, "distractor"))
            structural_examples.append(make_example("Incorrect premise: The reverse is true. " + prompt, rel_name, domain, "hard_negative"))

# STRUCTURAL_NEGATIVE: Same as STRUCTURAL + additional hard negatives
structural_negative_examples = list(structural_examples)
# Add extra hard negatives per relation (5 per relation, matching the remediation strategy)
hard_negative_templates = [
    "Incorrect premise: The opposite relationship holds. ",
    "False assumption: The direction is reversed. ",
    "Misleading: The intermediate step is different. ",
    "Wrong direction: The chain goes the other way. ",
    "Confusing: The entities are swapped. ",
]
for rel_name, rel_data in RELATIONS.items():
    for domain in rel_data["domains"]:
        triples = rel_data["domains"][domain]
        for triple in triples[:3]:  # 3 triples per domain
            if rel_name == "compositional_reasoning":
                prompt = rel_data["template"].format(A=triple[0], op1=triple[1], B=triple[2], op2=triple[3], C=triple[4], op3=triple[5], D=triple[6])
            elif rel_name == "analogical_mapping":
                prompt = rel_data["template"].format(A1=triple[0], B1=triple[1], A2=triple[2])
            else:
                prompt = rel_data["template"].format(A=triple[0], B=triple[1], C=triple[2])
            for hn_template in hard_negative_templates:
                structural_negative_examples.append(make_example(hn_template + prompt, rel_name, domain, "hard_negative_extra"))

# Balance to same count
target_count = len(control_examples)
# STRUCTURAL_NEGATIVE: may have more, trim
if len(structural_negative_examples) > target_count:
    structural_negative_examples = structural_negative_examples[:target_count]

print("CONTROL:", len(control_examples))
print("STRUCTURAL:", len(structural_examples))
print("STRUCTURAL_NEGATIVE:", len(structural_negative_examples))

# Write training data
for name, examples in [("control", control_examples), ("structural", structural_examples), ("structural_negative", structural_negative_examples)]:
    with open(OUT_DIR / f"{name}_training_data.jsonl", "w") as f:
        for ex in examples:
            f.write(json.dumps(ex) + "\n")

# Build evaluation surface (same for all arms)
eval_items = []

# SEEN combinations
for i, item in enumerate(control_examples):
    if i % 3 == 0:
        eval_items.append({
            "row_id": "seen_" + item["relation"] + "_" + item["domain"] + "_" + "{:03d}".format(i),
            "prompt": item["prompt"],
            "relation": item["relation"],
            "domain": item["domain"],
            "expected": item["expected"],
            "condition": "SEEN",
            "depth": 1
        })

# UNSEEN_COMBINATIONS
for rel_name, rel_data in RELATIONS.items():
    for domain, triples in rel_data["domains"].items():
        if len(triples) >= 3:
            for i in range(len(triples) - 1):
                t1, t2 = triples[i], triples[i+1]
                if rel_name == "compositional_reasoning":
                    new_prompt = rel_data["template"].format(A=t1[0], op1=t1[1], B=t1[2], op2=t1[3], C=t1[4], op3=t1[5], D=t2[2])
                elif rel_name == "analogical_mapping":
                    new_prompt = rel_data["template"].format(A1=t1[0], B1=t1[1], A2=t2[0])
                else:
                    new_prompt = rel_data["template"].format(A=t1[0], B=t2[1], C=t1[2])
                eval_items.append({
                    "row_id": "unseen_" + rel_name + "_" + domain + "_" + "{:03d}".format(i),
                    "prompt": new_prompt,
                    "relation": rel_name,
                    "domain": domain,
                    "expected": "yes",
                    "condition": "UNSEEN_COMBINATION",
                    "depth": 1
                })

# HELDOUT_DOMAIN (same relations, new domains)
for rel_name, rel_data in RELATIONS.items():
    heldout = rel_data["held_out"]
    first_domain = list(rel_data["domains"].keys())[0]
    triples = rel_data["domains"][first_domain]
    for triple in triples[:2]:
        if rel_name == "compositional_reasoning":
            prompt = rel_data["template"].format(A=triple[0], op1=triple[1], B=triple[2], op2=triple[3], C=triple[4], op3=triple[5], D=triple[6])
        elif rel_name == "analogical_mapping":
            prompt = rel_data["template"].format(A1=triple[0], B1=triple[1], A2=triple[2])
        else:
            prompt = rel_data["template"].format(A=triple[0], B=triple[1], C=triple[2])
        eval_items.append({
            "row_id": "heldout_" + rel_name + "_" + heldout + "_" + "{:03d}".format(triples.index(triple)),
            "prompt": prompt,
            "relation": rel_name,
            "domain": heldout,
            "expected": "yes",
            "condition": "HELDOUT_DOMAIN",
            "depth": 1
        })

# NOVEL_RELATION induction test
for rel_name, rel_data in NOVEL_RELATIONS.items():
    for domain, triples in rel_data["domains"].items():
        for triple in triples[:2]:
            prompt = rel_data["template"].format(A=triple[0], B=triple[1], C=triple[2])
            eval_items.append({
                "row_id": "novel_" + rel_name + "_" + domain + "_" + "{:03d}".format(triples.index(triple)),
                "prompt": prompt,
                "relation": rel_name,
                "domain": domain,
                "expected": "yes",
                "condition": "NOVEL_RELATION",
                "depth": 1
            })

# NOVEL_RELATION composition (2+ novel relations combined)
for rel_name, rel_data in NOVEL_RELATIONS.items():
    domain = list(rel_data["domains"].keys())[0]
    triples = rel_data["domains"][domain]
    if len(triples) >= 2:
        t1, t2 = triples[0], triples[1]
        prompt = "If " + t1[0] + " " + rel_name.replace("_", " ") + " " + t1[1] + ", and " + t1[1] + " " + rel_name.replace("_", " ") + " " + t2[2] + ", does " + t1[0] + " " + rel_name.replace("_", " ") + " " + t2[2] + "?"
        eval_items.append({
            "row_id": "novel_comp_" + rel_name + "_" + domain + "_001",
            "prompt": prompt,
            "relation": rel_name,
            "domain": domain,
            "expected": "yes",
            "condition": "NOVEL_COMPOSITION",
            "depth": 2
        })

# COUNTERFACTUAL
for rel_name, rel_data in RELATIONS.items():
    domain = list(rel_data["domains"].keys())[0]
    triples = rel_data["domains"][domain][:2]
    for j, triple in enumerate(triples):
        if rel_name == "compositional_reasoning":
            prompt = rel_data["template"].format(A=triple[0], op1=triple[1], B=triple[2], op2=triple[3], C=triple[4], op3=triple[5], D=triple[6])
        elif rel_name == "analogical_mapping":
            prompt = rel_data["template"].format(A1=triple[0], B1=triple[1], A2=triple[2])
        else:
            prompt = rel_data["template"].format(A=triple[0], B=triple[1], C=triple[2])
        cf_prompt = "Suppose the opposite were true: " + prompt
        eval_items.append({
            "row_id": "counterfactual_" + rel_name + "_" + domain + "_" + "{:03d}".format(j),
            "prompt": cf_prompt,
            "relation": rel_name,
            "domain": domain,
            "expected": "no",
            "condition": "COUNTERFACTUAL",
            "depth": 1
        })

# DISTRACTOR
distractors = ["Note that the sky appears blue during the day.", "Remember that water boils at 100 degrees Celsius."]
for rel_name, rel_data in RELATIONS.items():
    domain = list(rel_data["domains"].keys())[0]
    triples = rel_data["domains"][domain][:2]
    for j, triple in enumerate(triples):
        if rel_name == "compositional_reasoning":
            prompt = rel_data["template"].format(A=triple[0], op1=triple[1], B=triple[2], op2=triple[3], C=triple[4], op3=triple[5], D=triple[6])
        elif rel_name == "analogical_mapping":
            prompt = rel_data["template"].format(A1=triple[0], B1=triple[1], A2=triple[2])
        else:
            prompt = rel_data["template"].format(A=triple[0], B=triple[1], C=triple[2])
        dist_prompt = distractors[j % len(distractors)] + " " + prompt
        eval_items.append({
            "row_id": "distractor_" + rel_name + "_" + domain + "_" + "{:03d}".format(j),
            "prompt": dist_prompt,
            "relation": rel_name,
            "domain": domain,
            "expected": "yes",
            "condition": "DISTRACTOR",
            "depth": 1
        })

# DEPTH
for rel_name, rel_data in RELATIONS.items():
    domain = list(rel_data["domains"].keys())[0]
    triples = rel_data["domains"][domain]
    if len(triples) >= 4:
        for depth in [2, 3, 4]:
            if depth == 2:
                if rel_name == "compositional_reasoning":
                    prompt = rel_data["template"].format(A=triples[0][0], op1=triples[0][1], B=triples[0][2], op2=triples[0][3], C=triples[0][4], op3=triples[0][5], D=triples[0][6])
                elif rel_name == "analogical_mapping":
                    prompt = rel_data["template"].format(A1=triples[0][0], B1=triples[0][1], A2=triples[0][2])
                else:
                    prompt = rel_data["template"].format(A=triples[0][0], B=triples[0][1], C=triples[0][2])
            elif depth == 3:
                prompt = "If " + triples[0][0] + " causes " + triples[0][1] + ", " + triples[0][1] + " causes " + triples[0][2] + ", and " + triples[0][2] + " causes " + triples[1][0] + ", does " + triples[0][0] + " cause " + triples[1][0] + "?"
            else:
                prompt = "If " + triples[0][0] + " causes " + triples[0][1] + ", " + triples[0][1] + " causes " + triples[0][2] + ", " + triples[0][2] + " causes " + triples[1][0] + ", and " + triples[1][0] + " causes " + triples[1][1] + ", does " + triples[0][0] + " cause " + triples[1][1] + "?"
            eval_items.append({
                "row_id": "depth" + str(depth) + "_" + rel_name + "_" + domain + "_001",
                "prompt": prompt,
                "relation": rel_name,
                "domain": domain,
                "expected": "yes",
                "condition": "DEPTH",
                "depth": depth
            })

with open(OUT_DIR / "efficiency_eval.jsonl", "w") as f:
    for item in eval_items:
        f.write(json.dumps(item) + "\n")

with open(OUT_DIR / "efficiency_metadata.json", "w") as f:
    metadata = {
        "total_items": len(eval_items),
        "conditions": list(set(item["condition"] for item in eval_items)),
        "relations": list(RELATIONS.keys()) + list(NOVEL_RELATIONS.keys()),
        "domains": list(set(item["domain"] for item in eval_items)),
        "conditions_count": {}
    }
    from collections import Counter
    cond_counts = Counter(item["condition"] for item in eval_items)
    metadata["conditions_count"] = dict(cond_counts)
    json.dump(metadata, f, indent=2)

print("Evaluation surface built:")
print("Total items:", len(eval_items))
from collections import Counter
cond_counts = Counter(item["condition"] for item in eval_items)
for cond, count in cond_counts.items():
    print("  " + cond + ":", count)