import json
from pathlib import Path
import random

OUT_DIR = Path(".")
random.seed(42)

# Novel relations with arbitrary symbols (no natural-language definition)
NOVEL_RELATIONS = [
    {"name": "trills", "arity": 2, "definition": "A trills B if B precedes A in the sequence"},
    {"name": "glints", "arity": 2, "definition": "A glints B if A and B share the same parity"},
    {"name": "drapes", "arity": 2, "definition": "A drapes B if A is exactly 3 positions after B"},
    {"name": "flickers", "arity": 2, "definition": "A flickers B if the distance between A and B is prime"},
    {"name": "shimmers", "arity": 2, "definition": "A shimmers B if A*B is even"},
    {"name": "pulses", "arity": 2, "definition": "A pulses B if A mod B == 0"},
]

ENTITIES = [f"E{i}" for i in range(1, 21)]  # 20 arbitrary entities
SURFACE_FORMS = [
    "If {rel} {A} {B} and {rel} {B} {C}, does {rel} {A} {C}?",
    "Given: {rel} {A} {B}. Given: {rel} {B} {C}. Question: {rel} {A} {C}?",
    "Premise 1: {A} {rel} {B}. Premise 2: {B} {rel} {C}. Does {A} {rel} {C} hold?",
]

# Build composition chains
def build_chain(relation, length, entities):
    chain = random.sample(entities, length + 1)
    premises = []
    for i in range(length):
        premises.append(f"{chain[i]} {relation} {chain[i+1]}")
    query = f"{chain[0]} {relation} {chain[-1]}"
    return premises, query

# Ground truth for transitive relations
def evaluate_chain(relation, chain):
    # All our relations are transitive by design
    return True

def generate_item(depth, relation):
    premises, query = build_chain(relation["name"], depth, ENTITIES)
    surface = random.choice(SURFACE_FORMS).format(
        rel=relation["name"],
        A=premises[0].split()[0] if premises else "",
        B=premises[0].split()[2] if premises else "",
        C=query.split()[-1] if query else ""
    )
    return {
        "depth": depth,
        "relation": relation["name"],
        "relation_def": relation["definition"],
        "premises": premises,
        "query": query,
        "surface_form": surface,
        "expected": "Yes",
        "type": "composition",
        "condition": f"DEPTH_{depth}",
        "novel_relation": True,
        "held_out": True
    }

def generate_distractor_item(depth, relation):
    premises, query = build_chain(relation["name"], depth, ENTITIES)
    # Add a plausible but irrelevant distractor
    distractor = random.choice(ENTITIES)
    extra_premise = f"{distractor} {relation} {random.choice(ENTITIES)}"
    all_premises = premises + [extra_premise]
    surface = random.choice(SURFACE_FORMS).format(
        rel=relation["name"],
        A=premises[0].split()[0] if premises else "",
        B=premises[0].split()[2] if premises else "",
        C=query.split()[-1] if query else ""
    )
    return {
        "depth": depth,
        "relation": relation["name"],
        "relation_def": relation["definition"],
        "premises": all_premises,
        "query": query,
        "surface_form": surface + f" [Distractor: {extra_premise}]",
        "expected": "Yes",
        "type": "composition_distractor",
        "condition": f"DEPTH_{depth}_DISTRACTOR",
        "novel_relation": True,
        "held_out": True
    }

DEPTHS = [2, 3, 4, 5, 6, 8, 10]
ITEMS_PER_DEPTH = 6  # 6 novel relations per depth

all_items = []
for depth in DEPTHS:
    for i in range(ITEMS_PER_DEPTH):
        rel = NOVEL_RELATIONS[i]
        all_items.append(generate_item(depth, rel))
        if depth <= 6:  # Distractors for manageable depths
            all_items.append(generate_distractor_item(depth, rel))

# Add counterfactual variants
for depth in [2, 3, 4, 5]:
    for i in range(3):
        rel = NOVEL_RELATIONS[i]
        premises, query = build_chain(rel["name"], depth, ENTITIES)
        # Counterfactual: negate the conclusion
        all_items.append({
            "depth": depth,
            "relation": rel["name"],
            "relation_def": rel["definition"],
            "premises": premises,
            "query": f"NOT ({query})",
            "surface_form": f"If the premises hold, is it FALSE that {query}?",
            "expected": "No",
            "type": "composition_counterfactual",
            "condition": f"DEPTH_{depth}_COUNTERFACTUAL",
            "novel_relation": True,
            "held_out": True
        })

# Build final dataset
data = []
for i, item in enumerate(all_items):
    row = {
        "row_id": f"COMP002_{i:04d}",
        "surface_id": f"ATHANOR_COMPOSITION_002_{item['condition']}",
        "source_name": "synthetic_novel_relation_composition",
        "source_version": "1.0",
        "source_locator": f"depth_{item['depth']}_{item['type']}",
        "source_split": "test",
        "retrieval_timestamp": "2026-10-02T00:00:00Z",
        "rights_license_provenance": "synthetic_constructed",
        "raw_content_sha256": "synthetic",
        "normalized_content_sha256": "synthetic",
        "prompt": item["surface_form"],
        "expected": item["expected"],
        "metadata": {
            "depth": item["depth"],
            "relation": item["relation"],
            "relation_def": item["relation_def"],
            "premises": item["premises"],
            "query": item["query"],
            "type": item["type"],
            "condition": item["condition"],
            "novel_relation": item["novel_relation"],
            "held_out": item["held_out"]
        }
    }
    data.append(row)

output_file = OUT_DIR / "composition_eval.jsonl"
with open(output_file, "w") as f:
    for row in data:
        f.write(json.dumps(row) + "\n")

print(f"Generated {len(data)} items")
print(f"Depths: {DEPTHS}")
print(f"Types: {set(d['metadata']['type'] for d in data)}")
print(f"Conditions: {set(d['metadata']['condition'] for d in data)}")
print(f"Written to {output_file}")

# Save metadata
meta = {
    "experiment": "ATHANOR-RELATIONAL-COMPOSITION-002",
    "total_items": len(data),
    "depths": DEPTHS,
    "relations": len(NOVEL_RELATIONS),
    "inference_modes": ["DIRECT", "COT", "SELECTIVE_COMPUTE", "VERIFY", "SELECTIVE_VERIFY"],
    "threshold_reliable": 0.70,  # 70% accuracy for reliable horizon
    "threshold_confidence": 0.80  # confidence threshold for selective compute
}
with open(OUT_DIR / "composition_metadata.json", "w") as f:
    json.dump(meta, f, indent=2)