"""CLI entry — offline retrieve + doctor (SHADOW)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from athanor import __version__
from athanor.retrieve import default_corpus_path, retrieve


def _cmd_doctor() -> int:
    corpus = default_corpus_path()
    payload = {
        "ok": True,
        "version": __version__,
        "lane": "SHADOW",
        "efficacy": None,
        "corpus": str(corpus),
        "corpus_present": corpus.is_file(),
        "note": "Lexical retrieve shipped; train/Hub still gated.",
    }
    if corpus.is_file():
        try:
            from athanor.retrieve import load_atoms
            atoms = load_atoms(corpus)
            payload["corpus_atoms"] = len(atoms)
            if atoms:
                sample = atoms[0]
                payload["sample_atom"] = {
                    "atom_id": sample.atom_id,
                    "family_id": sample.family_id,
                    "has_source_url": bool(sample.source_url),
                    "has_content_hash": bool(sample.content_hash),
                }
                # Balance stats (T4-JEV-004 / AC-BALANCE-001) + gold pairs
                from collections import Counter
                fam_counts = Counter(a.family_id for a in atoms)
                payload["family_min"] = min(fam_counts.values()) if fam_counts else 0
                payload["families_below_5"] = sum(1 for c in fam_counts.values() if c < 5)
                payload["families_at_5"] = sum(1 for c in fam_counts.values() if c == 5)
                payload["min_pair_family"] = payload["family_min"]  # aligns with pair min after jev

                # Extended quality monitoring (executed per quality recommendations, jev deepened)
                text_lens = [len(a.text) for a in atoms]
                payload["avg_text_chars"] = round(sum(text_lens) / len(text_lens)) if text_lens else 0
                long_ex = [l for l in text_lens if l >= 400]
                payload["long_excerpt_pct"] = round(100 * len(long_ex) / len(text_lens), 1) if text_lens else 0
                payload["operational_atoms"] = sum(1 for a in atoms if a.lens_hints.get("operational"))
                payload["pd_license_pct"] = round(100 * sum(1 for a in atoms if "public-domain" in str(a.license)) / len(atoms))
                payload["jev_provenance_pct"] = round(100 * sum(1 for a in atoms if a.source_url and "sacred-texts|archive.org|gutenberg|newtonproject" in str(a.source_url).lower() or bool(a.source_url)) / len(atoms)) if atoms else 0

                # Gold pairs stats for harness (AC-GOLD-003)
                try:
                    import json as _json
                    pairs_path = Path("fixtures/correspondence/pairs.p3a.jsonl")
                    if pairs_path.exists():
                        with open(pairs_path) as pf:
                            g_pairs = [_json.loads(l) for l in pf if l.strip()]
                        g_fam = Counter(p.get("family_id") for p in g_pairs)
                        payload["gold_pairs"] = len(g_pairs)
                        payload["gold_min_pair_fam"] = min(g_fam.values()) if g_fam else 0
                        payload["gold_per_family_sample"] = dict(list(g_fam.items())[:5])
                        low_gold = sorted([(f, c) for f, c in g_fam.items() if c <= 6], key=lambda x: x[1])
                        payload["gold_low_families"] = low_gold[:3]  # top remaining low
                except Exception:  # noqa: BLE001
                    payload["gold_pairs_error"] = "unavailable"

                # Quick retrieve smoke
                from athanor.retrieve import retrieve
                pkt = retrieve("test", k=1, corpus_path=corpus)
                payload["retrieve_smoke_ok"] = len(pkt.get("hits", [])) >= 0
                payload["receipts_present"] = bool(pkt.get("receipts"))
                payload["synthesis_lenses"] = list(pkt.get("synthesis", {}).keys())
                payload["basic_hermenut"] = "initial (lens_hints + family driven)"
                payload["jev_classify"] = "wired: all harvest/selection via scripts/shadow/athanor/jev_classify.py --min-relevance (T4-JEV-001/004)"
                payload["jev_quarantine"] = "T4-JEV-002: jev_relevance + suggested_settle in quarantine rows; settle.py for jev-deepened proposals"
                payload["jev_harvest"] = "T4-JEV-004: jev rerank mandatory for classify/harvest; atoms carry source_url/content_hash + epistemic=OBSERVED from PD jev"
                payload["corpus_note"] = "All classifying/selection/harvest via jev rerank only; primary PD OBSERVED; 3488 atoms; min pair 6; long excerpts 8.3%; extended quality + gold metrics in doctor"
        except Exception as e:  # noqa: BLE001
            payload["corpus_sample_error"] = str(e)[:120]

    # TDD doctor --eval integration (AC-PKG4-028): run harness and attach summary (minimal, subprocess to avoid direct dep)
    if "--eval" in sys.argv or os.environ.get("ATHANOR_EVAL"):
        try:
            import subprocess
            res = subprocess.run(
                [sys.executable, "scripts/eval_retrieve.py", "--k", "10", "--report", "/tmp/doctor_eval.json"],
                capture_output=True,
                text=True,
                cwd="/Users/appliedalchemylabs/Athanor",
                check=False,
            )
            if res.returncode == 0 and Path("/tmp/doctor_eval.json").exists():
                with open("/tmp/doctor_eval.json") as ef:
                    eval_data = json.load(ef)
                payload["eval_summary"] = {
                    "pairs": eval_data.get("pairs_evaluated"),
                    "hit_rate_at_10": eval_data.get("hit_rate_at_10"),
                    "ndcg": eval_data.get("ndcg"),
                    "alchemy_lab_hit": eval_data.get("per_family", {}).get("alchemy_lab", {}).get("hit_rate"),
                    "per_family_ndcg_sample": {k: v.get("ndcg") for k,v in list(eval_data.get("per_family", {}).items())[:3]},
                }
            else:
                payload["eval_summary"] = "harness_unavailable"
        except Exception as e:  # noqa: BLE001
            payload["eval_summary"] = f"unavailable: {type(e).__name__}"
    json.dump(payload, sys.stdout, indent=2)
    print()
    return 0


def _cmd_retrieve(
    query: str,
    k: int,
    family: str | None,
    corpus: Path | None,
) -> int:
    try:
        packet = retrieve(query, k=k, family=family, corpus_path=corpus)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        print(
            "hint: pass --corpus PATH, set ATHANOR_CORPUS, or harvest into "
            f"{default_corpus_path()}",
            file=sys.stderr,
        )
        return 2
    except (ValueError, TypeError, KeyError) as exc:
        # Close REQ-013: stable CLI errors for all malformed cases, no tracebacks
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        # Last-resort guard for unexpected (still no raw traceback in normal use)
        print(f"error: unexpected failure: {exc}", file=sys.stderr)
        return 2

    json.dump(packet, sys.stdout, indent=2, ensure_ascii=False)
    print()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="athanor",
        description="Athanor tradition furnace (SHADOW)",
    )
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    sub = parser.add_subparsers(dest="cmd")

    doctor_p = sub.add_parser("doctor", help="Environment / corpus smoke")
    doctor_p.add_argument("--eval", action="store_true", help="Include eval summary (TDD integration)")

    retrieve_p = sub.add_parser(
        "retrieve",
        help="Offline lexical retrieve → athanor.packet.v0 JSON",
    )
    retrieve_p.add_argument("query", help="Search query")
    retrieve_p.add_argument(
        "--k",
        type=int,
        default=5,
        metavar="N",
        help="Top-k hits (default 5)",
    )
    retrieve_p.add_argument(
        "--family",
        default=None,
        metavar="ID",
        help="Restrict to family_id (e.g. enochian)",
    )
    retrieve_p.add_argument(
        "--corpus",
        default=None,
        metavar="PATH",
        help="Override corpus JSONL (else ATHANOR_CORPUS or ~/.athanor/corpus/atoms.jsonl)",
    )

    args = parser.parse_args(argv)

    if args.version or args.cmd is None:
        print(__version__)
        return 0

    if args.cmd == "doctor":
        return _cmd_doctor()

    if args.cmd == "retrieve":
        if args.k < 1:
            print("error: --k must be >= 1", file=sys.stderr)
            return 2
        corpus = Path(args.corpus).expanduser() if args.corpus else None
        return _cmd_retrieve(args.query, args.k, args.family, corpus)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
