"""Read-only local runtime inventory. Never downloads, loads weights, or trains."""
import argparse
import importlib.metadata
import json
import platform
import shutil
import subprocess
from pathlib import Path

from athanor.adapter_data import digest
from athanor.readiness import _json


def inspect_model(model_dir):
    """Inspect bounded configuration only; a directory name is not revision proof."""
    result = {"architecture": "NOT_COMPUTABLE", "config_sha256": None,
              "revision_verified": False, "weights_verified": False}
    if model_dir is None:
        return result
    path = Path(model_dir) / "config.json"
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 1024 * 1024:
        raise ValueError("Missing, unsafe or oversized model config")
    raw = path.read_bytes()
    config = _json(raw)
    if not isinstance(config, dict):
        raise TypeError("Model config must be an object")
    result.update(architecture=config.get("architectures", "NOT_COMPUTABLE"),
                  model_type=config.get("model_type", "NOT_COMPUTABLE"),
                  config_sha256=digest(raw.decode("utf-8")))
    return result


def inventory(model_dir=None):
    packages = {}
    for name in ("torch", "transformers", "peft", "trl", "accelerate", "bitsandbytes"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = "NOT_COMPUTABLE"
    gpu = {"status": "NOT_COMPUTABLE"}
    executable = shutil.which("nvidia-smi")
    if executable:
        try:
            run = subprocess.run(
                [executable, "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
                capture_output=True, text=True, timeout=15, check=False)
            gpu = {"exit_code": run.returncode,
                   "status": "OBSERVED" if run.returncode == 0 else "NOT_COMPUTABLE",
                   "devices": run.stdout.strip() if run.returncode == 0 else None}
        except (OSError, subprocess.TimeoutExpired):
            pass
    return {"schema_version": "athanor.runtime_inventory.v1", "status": "HOLD",
            "training_authorized": False, "system": platform.system(),
            "machine": platform.machine(), "python": platform.python_version(),
            "packages": packages, "gpu": gpu, "model": inspect_model(model_dir),
            "unresolved": ["PINNED_WEIGHT_REVISION", "REAL_TEMPLATE_MASK_TEST",
                           "BACKEND_COMPATIBILITY", "PEAK_MEMORY_SMOKE_TEST",
                           "REVIEWED_DATA_AND_RIGHTS", "TRAIN_APPROVAL"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", type=Path)
    args = parser.parse_args(argv)
    try:
        result = inventory(args.model_dir)
    except (ValueError, TypeError, OSError) as exc:
        print(json.dumps({"status": "INVALID", "reason": str(exc), "training_authorized": False}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
