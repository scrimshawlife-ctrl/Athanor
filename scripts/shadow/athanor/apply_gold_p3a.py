#!/usr/bin/env python3
"""Gold-settle P3a: stamp up to 400 KEEP atoms as OBSERVED (GOLD).

Mutates ~/.athanor/corpus/atoms.jsonl after backup.
Does NOT git-commit, Hub upload, harvest, or stamp HOLD as gold.
"""
from __future__ import annotations

import collections
import csv
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

ATOMS_PATH = Path.home() / ".athanor/corpus/atoms.jsonl"
CANDIDATES_CSV = Path("/workspace/athanor-harvest/settle/settle-candidates.csv")
SETTLE_DIR = Path.home() / ".athanor/settle"
RECEIPTS_DIR = Path.home() / ".athanor/receipts"
CARD_DIR = Path("/workspace/athanor-harvest/settle")
PROPOSAL_DIR = Path("/workspace/athanor-harvest/settle")

TARGET_GOLD = 400
ENOCHIAN_CAP = 40
FAMILY_SOFT_CAP = 28
BODY_MIN_PREFERRED = 500
BODY_MIN_OTHER = 800
BATCH = "gold-p3a-001"
PACK = "settle-pack-20260911-3000"
OPERATOR = "Danny continue 2026-09-11 PT"

CHROME_LOW = [
    "toggle sidebar", "toggle theme", "sign in", "buy usb", "close navigation",
    "view the original site", "internet sacred text archive", "donate",
    "search the archive", "support the archive", "buy the sacred texts usb",
    "own the wisdom of the ages", "ad free reading", "discussions are coming soon",
    "audiobooks are coming soon", "helps fund new texts", "no subscription",
    "evinity publishing", "a quiet place in cyberspace", "what's new?",
]
CLASSIC = {
    "the-demotic-magical-papyrus-of-london-and-leiden",
    "the-corpus-hermeticum",
    "the-i-ching",
}
PREFERRED_HOSTS = {"archive.org", "gutenberg", "sacred-texts"}


def utc_now():
    return datetime.now(timezone.utc)


def ts_compact(dt: datetime) -> str:
    return dt.strftime("%Y%m%dT%H%M%SZ")


def book_slug(url: str):
    m = re.search(r"/book/([^/?#]+)", url or "")
    return m.group(1).lower() if m else None


def host_of(url: str) -> str:
    u = url or ""
    if "archive.org" in u:
        return "archive.org"
    if "gutenberg.org" in u:
        return "gutenberg"
    if "notion" in u or u.startswith("file:"):
        return "operator"
    if "sacred-texts.com" in u:
        return "sacred-texts"
    return "other"


def strip_chrome(t: str) -> str:
    out = []
    for ln in t.splitlines():
        low = ln.lower()
        if "sacred-texts.com/categories" in low or "sacred-texts.com/shop/" in low:
            continue
        if any(m in low for m in CHROME_LOW) and len(ln) < 400:
            continue
        s = ln.lstrip()
        if s.startswith(("- [", "* [")) and "sacred-texts.com" in ln:
            continue
        if s.startswith(("[![", "![")):
            continue
        if low.lstrip().startswith("[home]"):
            continue
        if "membership" in low and "$10" in ln:
            continue
        head = s[3:].split(" ", 1)[0] if s.startswith("## ") else ""
        if head in ("Archive", "About", "Support", "Legal", "Membership", "Discussion"):
            continue
        if "Copyright" in ln and "Evinity" in ln:
            continue
        if low.lstrip().startswith("toggle theme"):
            continue
        if s.startswith("Section ") and len(s) < 40:
            continue
        if s.startswith("## Chapters"):
            continue
        if s.count(". ") >= 8 and sum(ch.isdigit() for ch in s) >= 10 and len(s) < 200:
            continue
        out.append(ln)
    body = " ".join(out)
    body = re.sub(
        r"\[[^\]\n]{0,80}\]\(https?://[^)\s]{0,120}(?:categories|/shop/|new\.htm)[^)\s]{0,80}\)",
        "",
        body,
    )
    return re.sub(r"\s+", " ", body).strip()


def preview(body: str, n: int = 200) -> str:
    return re.sub(r"\s+", " ", body[:n]).strip().replace('"', "'")


def score_row(r: dict) -> float:
    s = float(r["body_len"])
    if r["host"] == "archive.org":
        s += 300
    elif r["host"] == "gutenberg":
        s += 280
    elif r["host"] == "sacred-texts":
        s += 80
    if r["classic_book"]:
        s += 200
    if "/book/" in (r["source_url"] or "") and r["classic_book"]:
        s += 80
    if "index.htm" in (r["source_url"] or ""):
        s -= 800
    if r["chrome_frac"] < 0.15:
        s += 200
    s -= r["chrome_frac"] * 500
    prev = (r.get("preview") or "").lower()
    for bad in (
        "toggle theme",
        "table of contents",
        "usb drive",
        "membership",
        "section 1",
        "## chapters",
    ):
        if bad in prev:
            s -= 500
    s += sum(c.isalpha() for c in (r.get("preview") or "")) * 0.4
    return s


def load_candidates() -> dict[str, dict]:
    out = {}
    with CANDIDATES_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[row["atom_id"]] = row
    return out


def enrich(atom: dict, cand: dict | None) -> dict:
    url = atom.get("source_url") or (cand or {}).get("source_url") or ""
    text = atom.get("text") or ""
    body = strip_chrome(text)
    bl = len(body)
    raw = max(1, len(text))
    chrome_frac = 1.0 - (bl / raw)
    slug = book_slug(url)
    host = host_of(url)
    return {
        "atom_id": atom["atom_id"],
        "family_id": atom.get("family_id") or (cand or {}).get("family_id") or "",
        "source_url": url,
        "suggest": (cand or {}).get("suggest", "KEEP"),
        "reason": (cand or {}).get("reason", ""),
        "preview": (cand or {}).get("preview") or preview(body),
        "body_len": bl,
        "chrome_frac": round(chrome_frac, 3),
        "host": host,
        "slug": slug or "",
        "classic_book": bool(slug and slug in CLASSIC),
        "epistemic": atom.get("epistemic"),
    }


def eligible(r: dict) -> bool:
    if r["suggest"] != "KEEP":
        return False
    if r["epistemic"] == "OBSERVED":
        return False
    if r["host"] == "operator":
        return False
    if r["host"] in PREFERRED_HOSTS:
        return r["body_len"] >= BODY_MIN_PREFERRED
    return r["body_len"] >= BODY_MIN_OTHER


def select_gold(rows: list[dict]) -> list[dict]:
    ranked = sorted([r for r in rows if eligible(r)], key=score_row, reverse=True)
    chosen: list[dict] = []
    fam_n: collections.Counter = collections.Counter()
    enoch = 0
    deferred: list[dict] = []

    def try_add(r: dict, respect_soft: bool) -> bool:
        nonlocal enoch
        fid = r["family_id"]
        if fid == "enochian" and enoch >= ENOCHIAN_CAP:
            return False
        if respect_soft and fam_n[fid] >= FAMILY_SOFT_CAP:
            return False
        if len(chosen) >= TARGET_GOLD:
            return False
        chosen.append(r)
        fam_n[fid] += 1
        if fid == "enochian":
            enoch += 1
        return True

    for r in ranked:
        if len(chosen) >= TARGET_GOLD:
            break
        if not try_add(r, respect_soft=True):
            deferred.append(r)

    # Soft refill: if under target, allow over soft family cap but keep enochian hard cap
    if len(chosen) < TARGET_GOLD:
        chosen_ids = {x["atom_id"] for x in chosen}
        for r in ranked:
            if len(chosen) >= TARGET_GOLD:
                break
            if r["atom_id"] in chosen_ids:
                continue
            try_add(r, respect_soft=False)

    return chosen


def write_jsonl(path: Path, rows: list[dict], fields: list[str] | None = None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            if fields:
                f.write(json.dumps({k: r.get(k) for k in fields}, ensure_ascii=False) + "\n")
            else:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_proposal_only(gold_rows: list[dict], keep_rows: list[dict], hold_rows: list[dict], now: datetime):
    """Fallback when corpus mutation is blocked."""
    ts = ts_compact(now)
    proposal = PROPOSAL_DIR / "gold-candidates.jsonl"
    fields = [
        "atom_id", "family_id", "source_url", "host", "body_len", "chrome_frac",
        "classic_book", "score", "suggest", "preview",
    ]
    scored = []
    for r in gold_rows:
        d = dict(r)
        d["score"] = round(score_row(r), 2)
        scored.append(d)
    write_jsonl(proposal, scored, fields)
    write_jsonl(SETTLE_DIR / "gold.jsonl", scored, fields)
    write_jsonl(
        SETTLE_DIR / "keep.jsonl",
        keep_rows,
        ["atom_id", "family_id", "source_url", "suggest", "reason", "preview", "body_len", "host"],
    )
    write_jsonl(
        SETTLE_DIR / "hold.jsonl",
        hold_rows,
        ["atom_id", "family_id", "source_url", "suggest", "reason", "preview", "body_len", "host"],
    )
    receipt = {
        "run_id": f"gold-settle-p3a-{ts}",
        "action": "gold_settle_proposal_only",
        "status": "BLOCKED_NO_MUTATION",
        "timestamp_utc": now.isoformat(),
        "batch": BATCH,
        "pack": PACK,
        "operator": OPERATOR,
        "proposed_gold_count": len(gold_rows),
        "enochian_gold": sum(1 for r in gold_rows if r["family_id"] == "enochian"),
        "family_counts": dict(collections.Counter(r["family_id"] for r in gold_rows)),
        "proposal_path": str(proposal),
        "note": "Corpus mutation blocked or skipped; proposal written without stamping atoms.",
    }
    receipt_path = RECEIPTS_DIR / f"gold-settle-p3a-{ts}.json"
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    card_path = CARD_DIR / f"gold-p3a-001-{ts}.md"
    card_path.write_text(
        "\n".join(
            [
                f"# Gold settle P3a proposal — {ts}",
                "",
                f"- **Status**: proposal only (no corpus mutation)",
                f"- **Proposed GOLD**: {len(gold_rows)}",
                f"- **Enochian GOLD**: {receipt['enochian_gold']} / {ENOCHIAN_CAP}",
                f"- **Proposal**: `{proposal}`",
                f"- **Receipt**: `{receipt_path}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return receipt_path, card_path, proposal


def main():
    now = utc_now()
    ts = ts_compact(now)
    settled_at = now.isoformat()

    SETTLE_DIR.mkdir(parents=True, exist_ok=True)
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    CARD_DIR.mkdir(parents=True, exist_ok=True)

    atoms = [json.loads(l) for l in ATOMS_PATH.open() if l.strip()]
    cands = load_candidates()
    print(f"loaded atoms={len(atoms)} candidates={len(cands)}", flush=True)

    hold_ids = {aid for aid, c in cands.items() if c.get("suggest") == "HOLD"}
    keep_ids = {aid for aid, c in cands.items() if c.get("suggest") == "KEEP"}

    enriched: list[dict] = []
    atom_by_id = {}
    for a in atoms:
        atom_by_id[a["atom_id"]] = a
        cand = cands.get(a["atom_id"])
        # If atom not in CSV (shouldn't happen for keeps), treat carefully
        r = enrich(a, cand)
        # Force HOLD skip even if CSV missing — never gold HOLD
        if a["atom_id"] in hold_ids:
            r["suggest"] = "HOLD"
        elif cand is None:
            # only KEEP if it looks like preferred host substantial — but task says use CSV KEEP
            r["suggest"] = "HOLD"  # unknown → don't gold
        enriched.append(r)

    gold_rows = select_gold(enriched)
    gold_ids = {r["atom_id"] for r in gold_rows}
    # Safety: never include HOLD
    assert not (gold_ids & hold_ids), "HOLD leaked into gold"
    assert all(atom_by_id[i].get("epistemic") != "OBSERVED" for i in gold_ids)

    keep_rows = [r for r in enriched if r["atom_id"] in keep_ids or r["suggest"] == "KEEP"]
    hold_rows = [r for r in enriched if r["atom_id"] in hold_ids or r["suggest"] == "HOLD"]

    print(
        f"selected gold={len(gold_rows)} keep={len(keep_rows)} hold={len(hold_rows)} "
        f"enoch={sum(1 for r in gold_rows if r['family_id']=='enochian')} "
        f"families={len(set(r['family_id'] for r in gold_rows))}",
        flush=True,
    )

    # Write settle lists first (always)
    gold_out_fields = [
        "atom_id", "family_id", "source_url", "host", "body_len", "chrome_frac",
        "classic_book", "score", "preview",
    ]
    gold_scored = []
    for r in gold_rows:
        d = {k: r.get(k) for k in gold_out_fields if k != "score"}
        d["score"] = round(score_row(r), 2)
        d["decision"] = "GOLD"
        d["batch"] = BATCH
        gold_scored.append(d)

    write_jsonl(SETTLE_DIR / "gold.jsonl", gold_scored)
    write_jsonl(
        SETTLE_DIR / "keep.jsonl",
        keep_rows,
        ["atom_id", "family_id", "source_url", "suggest", "reason", "preview", "body_len", "host", "chrome_frac"],
    )
    write_jsonl(
        SETTLE_DIR / "hold.jsonl",
        hold_rows,
        ["atom_id", "family_id", "source_url", "suggest", "reason", "preview", "body_len", "host", "chrome_frac"],
    )
    # Also write proposal candidates mirror
    write_jsonl(PROPOSAL_DIR / "gold-candidates.jsonl", gold_scored)

    # Backup + mutate corpus
    backup_path = ATOMS_PATH.with_name(f"atoms.pre-gold-{ts}.jsonl")
    try:
        shutil.copy2(ATOMS_PATH, backup_path)
        print(f"backup {backup_path}", flush=True)

        settle_meta = {
            "decision": "GOLD",
            "batch": BATCH,
            "pack": PACK,
            "operator": OPERATOR,
            "settled_at": settled_at,
        }
        new_atoms = []
        stamped = 0
        for a in atoms:
            if a["atom_id"] in gold_ids:
                # Never stamp HOLD
                if a["atom_id"] in hold_ids:
                    raise RuntimeError(f"refusing to stamp HOLD as gold: {a['atom_id']}")
                a = dict(a)
                a["epistemic"] = "OBSERVED"
                a["settle"] = dict(settle_meta)
                stamped += 1
            new_atoms.append(a)

        tmp = ATOMS_PATH.with_suffix(".jsonl.tmp-gold")
        with tmp.open("w", encoding="utf-8") as f:
            for a in new_atoms:
                f.write(json.dumps(a, ensure_ascii=False) + "\n")
        tmp.replace(ATOMS_PATH)
        print(f"stamped {stamped} atoms -> OBSERVED", flush=True)
        mutated = True
        block_note = None
    except Exception as e:
        # If mutation fails (permissions etc.), leave proposal artifacts
        mutated = False
        block_note = str(e)
        print(f"MUTATION_FAILED: {e}", flush=True)
        receipt_path, card_path, proposal = write_proposal_only(gold_rows, keep_rows, hold_rows, now)
        print(json.dumps({
            "status": "proposal_only",
            "reason": block_note,
            "gold": len(gold_rows),
            "receipt": str(receipt_path),
            "card": str(card_path),
            "proposal": str(proposal),
        }, indent=2))
        return

    # Re-read epistemic totals
    ep = collections.Counter()
    with ATOMS_PATH.open() as f:
        n_lines = 0
        for line in f:
            if not line.strip():
                continue
            n_lines += 1
            ep[json.loads(line).get("epistemic", "?")] += 1
    sha_after = hashlib.sha256(ATOMS_PATH.read_bytes()).hexdigest()
    fam_counts = collections.Counter(r["family_id"] for r in gold_rows)
    host_counts = collections.Counter(r["host"] for r in gold_rows)
    enoch_gold = fam_counts.get("enochian", 0)

    receipt = {
        "run_id": f"gold-settle-p3a-{ts}",
        "action": "gold_settle_p3a",
        "status": "APPLIED",
        "timestamp_utc": settled_at,
        "batch": BATCH,
        "pack": PACK,
        "operator": OPERATOR,
        "before_count": len(atoms),
        "after_count": n_lines,
        "gold_count": stamped,
        "enochian_gold": enoch_gold,
        "enochian_cap": ENOCHIAN_CAP,
        "family_soft_cap": FAMILY_SOFT_CAP,
        "family_count": len(fam_counts),
        "family_counts": dict(fam_counts.most_common()),
        "host_counts": dict(host_counts.most_common()),
        "epistemic_after": dict(ep),
        "backup": str(backup_path),
        "corpus_sha256_after": sha_after,
        "settle_paths": {
            "gold": str(SETTLE_DIR / "gold.jsonl"),
            "keep": str(SETTLE_DIR / "keep.jsonl"),
            "hold": str(SETTLE_DIR / "hold.jsonl"),
            "candidates": str(PROPOSAL_DIR / "gold-candidates.jsonl"),
        },
        "selection": {
            "body_min_preferred_hosts": BODY_MIN_PREFERRED,
            "body_min_other": BODY_MIN_OTHER,
            "preferred_hosts": sorted(PREFERRED_HOSTS),
            "skipped_hold": True,
            "skipped_operator": True,
            "skipped_already_observed": True,
        },
        "gold_atom_ids": sorted(gold_ids),
        "no_git_commit": True,
        "no_hub_upload": True,
        "no_harvest": True,
    }
    receipt_path = RECEIPTS_DIR / f"gold-settle-p3a-{ts}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Card
    L = []
    A = L.append
    A(f"# Gold settle P3a — {BATCH} — {ts}")
    A("")
    A(f"- **Operator**: {OPERATOR}")
    A(f"- **Pack**: `{PACK}`")
    A(f"- **Corpus**: {n_lines} atoms (backup `{backup_path.name}`)")
    A(f"- **GOLD stamped**: **{stamped}** → `epistemic=OBSERVED`")
    A(f"- **Families in GOLD**: {len(fam_counts)}")
    A(f"- **Enochian GOLD**: {enoch_gold} / {ENOCHIAN_CAP} cap")
    A(f"- **Epistemic after**: OBSERVED={ep.get('OBSERVED', 0)} · INFERRED={ep.get('INFERRED', 0)}")
    A(f"- **Hosts**: " + " · ".join(f"{h} {n}" for h, n in host_counts.most_common()))
    A(f"- **sha256 after**: `{sha_after}`")
    A(f"- **Receipt**: `{receipt_path}`")
    A(f"- **Settle lists**: `~/.athanor/settle/{{gold,keep,hold}}.jsonl`")
    A("")
    A("## Policy applied")
    A("")
    A(f"- KEEP only; HOLD skipped; operator host skipped; already OBSERVED skipped")
    A(f"- body_len ≥ {BODY_MIN_PREFERRED} on archive.org|gutenberg|sacred-texts; ≥ {BODY_MIN_OTHER} other")
    A(f"- Enochian hard cap {ENOCHIAN_CAP}; soft per-family cap {FAMILY_SOFT_CAP}")
    A("- Prefer archive.org / gutenberg / classic `/book/` PD; score = body_len + host bonuses − chrome_frac")
    A("- No git commit · no Hub upload · no further harvest")
    A("")
    A("## GOLD by family")
    A("")
    A("| family_id | n |")
    A("|---|---:|")
    for fam, n in fam_counts.most_common():
        A(f"| `{fam}` | {n} |")
    A("")
    A("## Top 25 GOLD (by score)")
    A("")
    A("| atom_id | family | host | body_len | score | preview |")
    A("|---|---|---|---:|---:|---|")
    top = sorted(gold_rows, key=score_row, reverse=True)[:25]
    for r in top:
        A(
            f"| `{r['atom_id']}` | `{r['family_id']}` | {r['host']} | {r['body_len']} | "
            f"{score_row(r):.0f} | {preview(r.get('preview') or '', 120).replace('|', '/')} |"
        )
    A("")
    card_path = CARD_DIR / f"gold-p3a-001-{ts}.md"
    card_path.write_text("\n".join(L) + "\n", encoding="utf-8")

    summary = {
        "status": "APPLIED",
        "gold_count": stamped,
        "family_count": len(fam_counts),
        "enochian_gold": enoch_gold,
        "OBSERVED": ep.get("OBSERVED", 0),
        "INFERRED": ep.get("INFERRED", 0),
        "corpus_wc": n_lines,
        "receipt": str(receipt_path),
        "card": str(card_path),
        "backup": str(backup_path),
        "sha256": sha_after,
        "family_counts": dict(fam_counts.most_common()),
    }
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
