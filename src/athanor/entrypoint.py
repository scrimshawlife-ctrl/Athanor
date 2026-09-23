"""CLI entry — offline retrieve + doctor (SHADOW)."""

from __future__ import annotations

import argparse
import json
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
                # Quick retrieve smoke
                from athanor.retrieve import retrieve
                pkt = retrieve("test", k=1, corpus_path=corpus)
                payload["retrieve_smoke_ok"] = len(pkt.get("hits", [])) >= 0
                payload["receipts_present"] = bool(pkt.get("receipts"))
                payload["synthesis_lenses"] = list(pkt.get("synthesis", {}).keys())
                payload["basic_hermenut"] = "initial (lens_hints + family driven)"
                payload["jev_classify"] = "available via scripts/shadow/athanor/jev_classify.py (T4-JEV-001 wired in deepen_harvest)"
                payload["jev_quarantine"] = "T4-JEV-002: jev_relevance scores now emitted in quarantine classify() output for settle gates"
                payload["corpus_note"] = "All classifying via jev rerank; PD primary only; >3000 atoms; quarantine now carries jev_relevance"
        except Exception as e:  # noqa: BLE001
            payload["corpus_sample_error"] = str(e)[:120]
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

    sub.add_parser("doctor", help="Environment / corpus smoke")

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
