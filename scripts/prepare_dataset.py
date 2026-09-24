#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from athanor.dataset import prepare_dataset

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--gold", type=Path, required=True)
    p.add_argument("--weak", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    try:
        prepare_dataset(args.gold, args.weak, args.out, {"train":0.8,"eval":0.2})
        print("FROZEN (but HOLD per policy)")
    except SystemExit as e:
        print(f"HOLD: exit {e.code}", file=sys.stderr)
        sys.exit(e.code or 2)
    except Exception as e:
        print(f"HOLD: {e}", file=sys.stderr)
        sys.exit(2)
if __name__ == "__main__":
    main()
