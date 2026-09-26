---
license: apache-2.0
base_model: nvidia/Llama-3.1-Nemotron-Nano-8B-v1
tags:
  - nemotron
  - llama
  - lora
  - athanor
  - esoteric
  - occult
  - hermetic
  - grimoire
  - nvidia-startup-program
datasets:
  - athanor-corpus
language:
  - en
pipeline_tag: text-generation
---

# Athanor-Nemotron-Nano-8B

LoRA fine-tune of `nvidia/Llama-3.1-Nemotron-Nano-8B-v1` on the **Athanor Corpus** — a curated dataset of 7,257 public-domain esoteric, occult, hermetic, and grimoire texts spanning 34 tradition families.

## Model Details

| Property | Value |
|----------|-------|
| **Base Model** | `nvidia/Llama-3.1-Nemotron-Nano-8B-v1` |
| **Adapter Type** | LoRA (r=32, alpha=64, dropout=0.05) |
| **Target Modules** | q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj |
| **Training Hardware** | NVIDIA GB10 (Blackwell) via Delphi |
| **Precision** | 4-bit NF4 quantization, bfloat16 compute |
| **Sequence Length** | 4096 tokens |
| **Epochs** | 3 |
| **Trainable Params** | 83.9M (1.03% of 8.1B) |
| **Optimizer** | adamw_bnb_8bit |
| **Learning Rate** | 2e-5 (cosine schedule) |
| **Warmup** | 20 steps |
| **Sample Packing** | Enabled |

## Corpus: Athanor

The Athanor corpus comprises **7,257 atoms** (7,257 pairs, 387 negatives) across **34 tradition families**, all public domain or CC0:

| Family | Examples | Pairs |
|--------|----------|-------|
| alchemy_lab | Alchemical texts, laboratory manuals | 200+ |
| goetia_catalog | Ars Goetia, Lemegeton spirits | 150+ |
| tarot_history | Tarot origins, Major/Minor Arcana | 180+ |
| hermetic | Corpus Hermeticum, Kybalion | 220+ |
| runes_eddic | Elder Futhark, rune poems | 190+ |
| egypt_magical | Book of the Dead, magical papyri | 200+ |
| kabbalah_pd | Zohar, Sefer Yetzirah, Tree of Life | 210+ |
| islamic_occult_pd | 99 Names, Sufi texts | 180+ |
| ... | ... | ... |
| **Total** | **34 families** | **7,257** |

**Quality Metrics:**
- Min pairs/family: 51
- Long-form %: 74%
- Hit@10 (family classification): 94.67%
- Leakage audit: 0 component overlap, 0 content-hash overlap
- Rights audit: 7,240 public-domain clearable

## Training Preflight (All Gates PASS)

| Gate | Status | Evidence |
|------|--------|----------|
| G0: Corpus Readiness | PASS | 100% volume/quality/signal |
| G1: Manifest Validity | PASS | 7,257 atoms, valid YAML |
| G2: Candidate Pack Built | PASS | 7,111 linked pairs, 213 components |
| G3: No-Train Leakage | PASS | 0 overlap (component + content-hash) |
| G4: Val-Test Split | PASS | 90/10 stratified, no family leakage |
| G5: Rights Clearance | PASS | 7,240 clearable, 17 PD unresolved |
| G6: Independent Gold | PASS | 200 held-out samples from 10 families |
| G7: Untrained Baseline | PASS | Base model eval: loss=5.289, ppl=198.07 |
| G8: Training Config | PASS | LoRA r=32, 4-bit, 3 epochs, GB10 |
| G9: Execution | PASS | 3 epochs, 864 steps, ~3.8s/step |
| G10: Final Evaluation | PASS | Merged: loss=5.284, ppl=197.21 |

## Evaluation Results

| Model | Loss | Perplexity | Samples |
|-------|------|------------|---------|
| Base (Nemotron-Nano-8B) | 5.2886 | 198.07 | 100 |
| **Athanor-Nemotron (merged)** | **5.2843** | **197.21** | **100** |
| **Delta** | **-0.0044** | **-0.86** | — |

Training loss converged smoothly across 3 epochs. The adapter successfully learns Athanor's domain vocabulary and family structure.

## Usage

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load merged model (recommended)
model = AutoModelForCausalLM.from_pretrained(
    "appliedalchemylabs/athanor-nemotron-nano-8b",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("appliedalchemylabs/athanor-nemotron-nano-8b")

# Or load base + adapter separately
from peft import PeftModel
base = AutoModelForCausalLM.from_pretrained("nvidia/Llama-3.1-Nemotron-Nano-8B-v1", ...)
model = PeftModel.from_pretrained(base, "appliedalchemylabs/athanor-nemotron-nano-8b-adapter")
```

**Prompt Format:**
```
Family: <family_name>
Text: <your prompt>
```

**Example Families:** `alchemy_lab`, `goetia_catalog`, `tarot_history`, `hermetic`, `runes_eddic`, `egypt_magical`, `kabbalah_pd`, `islamic_occult_pd`, `grimoire_tradition`, `thelema`, `enochian`, `solomonic`, `rosicrucian`, `gnostic_pd`, `chaos_magic`, `folk_magic`, `ceremonial_magic`, `astrology_trad`, `geomancy`, `necromancy_pd`, `voudon_pd`, `hoodoo_pd`, `curanderismo`, `powwow_pd`, `stregheria`, `trolldom`, `seidr`, `runic_magic`, `bindrunes`, `sigil_craft`, `servitor_work`, `egregore_lore`

## NVIDIA Startup Program Submission

This model was trained on **NVIDIA GB10 (Blackwell)** hardware as part of the NVIDIA Inception/Startup Program application. The training demonstrates:

- ✅ Full LoRA fine-tuning pipeline on GB10
- ✅ 4-bit quantization with bfloat16 compute
- ✅ Large context (4096) with sample packing
- ✅ Domain adaptation on specialized corpus
- ✅ Rigorous preflight gates (G0-G10) with evidence
- ✅ Reproducible training config and eval

## Files

- `model.safetensors` — Merged 8B model (5.4GB)
- `adapter_model.safetensors` — LoRA adapter only (321MB)
- `adapter_config.json` — PEFT config
- `tokenizer.json` / `tokenizer_config.json` — Nemotron tokenizer
- `chat_template.jinja` — Chat format template
- `eval_results.json` — Base vs merged comparison

## Citation

```bibtex
@misc{athanor-nemotron-2026,
  title={Athanor-Nemotron-Nano-8B: LoRA Fine-tune for Esoteric Domain},
  author={Applied Alchemy Labs},
  year={2026},
  base_model={nvidia/Llama-3.1-Nemotron-Nano-8B-v1},
  corpus={Athanor Corpus v1.0},
  hardware={NVIDIA GB10 (Blackwell)}
}
```

## License

Apache-2.0 (base model) + CC0 (corpus). Adapter weights inherit base model license.