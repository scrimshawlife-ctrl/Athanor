import json
import math
import os
import random
import sys
from pathlib import Path

# Config
#
# These paths were absolute to the machine the training ran on (`/home/delphi`, Linux). They are read from the
# environment so the script can run wherever the artifacts actually are, and the defaults stay as they were so
# nothing on that machine changes. What this fixes is the failure mode: pointed at a machine without those
# artifacts, the script used to die somewhere inside `from_pretrained` with a confusing error. It now says
# what is missing and why. No trained adapter exists in this repository -- `adapter_preflight` reports it
# INVALID and `specs/003-qwen-adapter/model-lock.json` records `weight_downloaded: false`.
BASE_MODEL = os.environ.get("ATHANOR_BASE_MODEL", "nvidia/Llama-3.1-Nemotron-Nano-8B-v1")
ADAPTER_PATH = os.environ.get(
    "ATHANOR_ADAPTER_PATH", "/home/delphi/Athanor/lora-out-transfer-001-t1/checkpoint-48"
)
EVAL_FILE = os.environ.get(
    "ATHANOR_COMPOSITION_EVAL_FILE",
    "/home/delphi/Athanor/artifacts/composition/ATHANOR-RELATIONAL-COMPOSITION-002/composition_eval.jsonl",
)
OUT_DIR = Path(
    os.environ.get(
        "ATHANOR_COMPOSITION_OUT_DIR",
        "/home/delphi/Athanor/artifacts/composition/ATHANOR-RELATIONAL-COMPOSITION-002",
    )
)
THRESHOLD_RELIABLE = 0.70
THRESHOLD_CONFIDENCE = 0.80

_missing = [p for p in (ADAPTER_PATH, EVAL_FILE) if not Path(p).exists()]
if _missing:
    sys.exit(
        "Cannot run this evaluation: adapter and/or eval file not found.\n"
        + "\n".join(f"  missing: {p}" for p in _missing)
        + "\n\nThis script evaluated a trained LoRA adapter. No trained adapter artifacts are present (the\n"
        "training ran on another host). Point ATHANOR_ADAPTER_PATH and ATHANOR_COMPOSITION_EVAL_FILE at the\n"
        "real artifacts, or re-run training. For the runtime state of this machine, use:\n"
        "  python -m athanor.adapter_preflight"
    )

# The model stack is imported only once the artifacts are known to exist, so the failure names the real
# problem. Imported earlier, this file died on `ModuleNotFoundError: No module named 'torch'` and said nothing
# about the adapter it could not find either.
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load model
print("Loading model...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
tokenizer.pad_token = tokenizer.eos_token

base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True
)
model = PeftModel.from_pretrained(base_model, ADAPTER_PATH, is_trainable=False)
model.eval()
print("Model loaded.")

# Load evaluation data
with open(EVAL_FILE) as f:
    eval_data = [json.loads(line) for line in f]

def generate_response(prompt, mode="DIRECT", max_new_tokens=256, temperature=0.0):
    """Generate response with different inference modes."""
    
    if mode == "DIRECT":
        full_prompt = f"Answer the following question directly with Yes or No:\n{prompt}\nAnswer:"
        
    elif mode == "COT":
        full_prompt = f"Answer the following question by reasoning step by step. Then give your final answer as Yes or No:\n{prompt}\n\nReasoning:\n"
        
    elif mode == "VERIFY":
        full_prompt = f"Solve the following problem. For each premise, state whether it holds. Then verify each logical step. Finally answer Yes or No:\n{prompt}\n\nVerification:\n"
        
    elif mode == "SELECTIVE_COMPUTE":
        full_prompt = f"Think about this problem. If you are confident, answer directly. If uncertain, reason step by step. Then answer Yes or No:\n{prompt}\n\nAnswer:"
        
    elif mode == "SELECTIVE_VERIFY":
        full_prompt = f"Solve this problem. First, assess your confidence. If confident, answer directly. If uncertain, verify each step explicitly. Then answer Yes or No:\n{prompt}\n\nAssessment:\n"
    
    inputs = tokenizer(full_prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=temperature > 0,
            pad_token_id=tokenizer.eos_token_id,
            return_dict_in_generate=True,
            output_scores=True
        )
    
    generated = tokenizer.decode(outputs.sequences[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
    
    # Extract answer
    answer = "Unknown"
    if "Yes" in generated[:100]:
        answer = "Yes"
    elif "No" in generated[:100]:
        answer = "No"
    
    # Compute confidence (simple heuristic from token probabilities)
    scores = outputs.scores
    if scores:
        probs = [torch.softmax(s[0], dim=-1).max().item() for s in scores[:20]]
        confidence = sum(probs) / len(probs) if probs else 0.5
    else:
        confidence = 0.5
    
    return {
        "raw_output": generated,
        "answer": answer,
        "confidence": confidence,
        "tokens": len(outputs.sequences[0]) - inputs.input_ids.shape[1]
    }

# Run all modes
MODES = ["DIRECT", "COT", "SELECTIVE_COMPUTE", "VERIFY", "SELECTIVE_VERIFY"]
all_results = {}

for mode in MODES:
    print(f"\n=== Running {mode} ===")
    mode_results = []
    for item in eval_data:
        result = generate_response(item["prompt"], mode=mode)
        result["row_id"] = item["row_id"]
        result["expected"] = item["expected"]
        result["depth"] = item["metadata"]["depth"]
        result["type"] = item["metadata"]["type"]
        result["condition"] = item["metadata"]["condition"]
        result["relation"] = item["metadata"]["relation"]
        correct = result["answer"] == item["expected"]
        result["correct"] = correct
        mode_results.append(result)
    all_results[mode] = mode_results

# Compute metrics
def compute_metrics(results):
    by_depth = {}
    for r in results:
        d = r["depth"]
        if d not in by_depth:
            by_depth[d] = {"correct": 0, "total": 0, "confidences": [], "errors": []}
        by_depth[d]["total"] += 1
        if r["correct"]:
            by_depth[d]["correct"] += 1
        by_depth[d]["confidences"].append(r["confidence"])
        if not r["correct"]:
            by_depth[d]["errors"].append(r)
    
    metrics = {}
    for d in sorted(by_depth.keys()):
        stats = by_depth[d]
        acc = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
        avg_conf = sum(stats["confidences"]) / len(stats["confidences"]) if stats["confidences"] else 0
        metrics[d] = {
            "accuracy": acc,
            "avg_confidence": avg_conf,
            "n": stats["total"],
            "errors": len(stats["errors"])
        }
    return metrics

# Compute horizon
def find_horizon(metrics, threshold=0.70):
    for d in sorted(metrics.keys()):
        if metrics[d]["accuracy"] < threshold:
            return d - 1  # last depth that was reliable
    return max(metrics.keys())

# Compute all
summary = {}
for mode in MODES:
    metrics = compute_metrics(all_results[mode])
    horizon = find_horizon(metrics, THRESHOLD_RELIABLE)
    summary[mode] = {
        "horizon": horizon,
        "depth_metrics": metrics,
        "total_tokens": sum(r["tokens"] for r in all_results[mode]),
        "avg_tokens": sum(r["tokens"] for r in all_results[mode]) / len(all_results[mode])
    }
    print(f"{mode}: horizon={horizon}, metrics={metrics}")

# Save results
output = {
    "experiment": "ATHANOR-RELATIONAL-COMPOSITION-002",
    "model": "T1_BEST",
    "adapter_path": ADAPTER_PATH,
    "threshold_reliable": THRESHOLD_RELIABLE,
    "modes": summary,
    "raw_results": {k: v for k, v in all_results.items()}
}

with open(OUT_DIR / "composition_results.json", "w") as f:
    json.dump(output, f, indent=2)

print("\n=== FINAL HORIZONS ===")
for mode in MODES:
    print(f"{mode}: {summary[mode]['horizon']} hops")

print("\nResults saved.")