"""Offline lexical retrieve over local atom JSONL (Wave 0 frozen slice).

Stdlib-only BM25-ish ranking. Corpus default: ~/.athanor/corpus/atoms.jsonl
Override path with ATHANOR_CORPUS.

Excerpts run `strip_chrome` at retrieve time so sacred-texts SPA nav does not
own the window. Stored SoT atoms are not rewritten.
"""

from __future__ import annotations

import json
import math
import os
import re
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from athanor.chrome import strip_chrome

_TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
_DEFAULT_CORPUS = Path.home() / ".athanor" / "corpus" / "atoms.jsonl"
_EXCERPT_MAX = 280

# BM25 defaults (Robertson / Zaragoza)
_K1 = 1.2
_B = 0.75

_SYNTHESIS_STUBS: dict[str, dict[str, str]] = {
    "historical": {
        "text": "Retrieved atoms reflect documented tradition witnesses; "
        "dating and attribution follow source metadata when present.",
        "epistemic": "INFERRED",
    },
    "symbolic": {
        "text": "Hits are ranked by lexical overlap with the query; "
        "symbolic readings remain interpretive overlays on the cited text.",
        "epistemic": "INFERRED",
    },
    "operational": {
        "text": "Athanor returns historical/textual context only — "
        "no practice instructions, efficacy scores, or summon UX.",
        "epistemic": "INFERRED",
    },
}


@dataclass(frozen=True)
class Atom:
    atom_id: str
    family_id: str
    text: str
    license: str
    epistemic: str
    tokens: tuple[str, ...]
    source_url: str | None = None
    content_hash: str | None = None
    lens_hints: dict = field(default_factory=dict)  # from atom data for three-lens differentiation

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> Atom:
        text = str(raw.get("text") or "")
        # Strict required fields with clear error (closes REQ-013 deviation)
        if "atom_id" not in raw or not raw.get("atom_id"):
            raise ValueError("missing required field 'atom_id'")
        if "family_id" not in raw or not raw.get("family_id"):
            raise ValueError("missing required field 'family_id'")
        hints = raw.get("lens_hints") or {}
        if not isinstance(hints, dict):
            hints = {}
        return cls(
            atom_id=str(raw["atom_id"]),
            family_id=str(raw["family_id"]),
            text=text,
            license=str(raw.get("license") or "unknown"),
            epistemic=str(raw.get("epistemic") or "INFERRED"),
            tokens=tuple(tokenize(text)),
            source_url=raw.get("source_url"),
            content_hash=raw.get("content_hash"),
            lens_hints=hints,
        )


def tokenize(text: str) -> list[str]:
    return [m.group(0).lower() for m in _TOKEN_RE.finditer(text)]


def default_corpus_path() -> Path:
    override = os.environ.get("ATHANOR_CORPUS")
    if override:
        return Path(override).expanduser()
    return _DEFAULT_CORPUS


def load_atoms(path: Path | None = None) -> list[Atom]:
    corpus = path if path is not None else default_corpus_path()
    if not corpus.is_file():
        raise FileNotFoundError(f"corpus not found: {corpus}")

    atoms: list[Atom] = []
    with corpus.open(encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL at {corpus}:{line_no}") from exc
            if not isinstance(raw, dict):
                raise TypeError(f"atom must be object at {corpus}:{line_no}")
            try:
                atoms.append(Atom.from_mapping(raw))
            except (KeyError, ValueError) as exc:
                raise ValueError(f"invalid atom at {corpus}:{line_no}: {exc}") from exc
    return atoms


def _idf(n_docs: int, df: int) -> float:
    # BM25+ style smoothed IDF; never negative for tiny corpora.
    return math.log(1.0 + (n_docs - df + 0.5) / (df + 0.5))


def _bm25_scores(
    query_tokens: Sequence[str],
    atoms: Sequence[Atom],
) -> list[float]:
    if not atoms or not query_tokens:
        return [0.0] * len(atoms)

    n_docs = len(atoms)
    df: Counter[str] = Counter()
    for atom in atoms:
        df.update(set(atom.tokens))

    avgdl = sum(len(a.tokens) for a in atoms) / n_docs
    q_tf = Counter(query_tokens)
    idf_cache = {term: _idf(n_docs, df.get(term, 0)) for term in q_tf}

    scores: list[float] = []
    for atom in atoms:
        dl = len(atom.tokens) or 1
        tf_map = Counter(atom.tokens)
        score = 0.0
        for term, q_weight in q_tf.items():
            tf = tf_map.get(term, 0)
            if tf == 0:
                continue
            denom = tf + _K1 * (1.0 - _B + _B * (dl / avgdl))
            score += idf_cache[term] * q_weight * (tf * (_K1 + 1.0)) / denom
        scores.append(score)
    return scores


def _excerpt(text: str, query_tokens: Sequence[str], limit: int = _EXCERPT_MAX) -> str:
    compact = " ".join(strip_chrome(text).split())
    if not compact:
        return ""
    if len(compact) <= limit:
        return compact

    lower = compact.lower()
    best = 0
    for tok in query_tokens:
        idx = lower.find(tok)
        if idx >= 0:
            best = max(0, idx - limit // 4)
            break
    snippet = compact[best : best + limit]
    if best > 0:
        snippet = "…" + snippet
    if best + limit < len(compact):
        snippet = snippet.rstrip() + "…"
    return snippet


def rank_atoms(
    query: str,
    atoms: Sequence[Atom],
    *,
    k: int = 5,
    family: str | None = None,
) -> list[tuple[Atom, float]]:
    if k < 1:
        raise ValueError("k must be >= 1")

    pool: list[Atom] = list(atoms)
    if family:
        pool = [a for a in pool if a.family_id == family]

    q_tokens = tokenize(query)
    scores = _bm25_scores(q_tokens, pool)
    ranked = sorted(
        zip(pool, scores, strict=True),
        key=lambda pair: (-pair[1], pair[0].atom_id),
    )
    # Drop zero-score misses when the query had tokens (guard in retrieve() now rejects pure tokenless).
    if q_tokens:
        ranked = [pair for pair in ranked if pair[1] > 0.0]
    return ranked[:k]


def _build_lens_synthesis(atom: Atom, query: str) -> dict[str, dict[str, str]]:
    """Basic three-lens synthesis using atom data (initial HERMENEUT wiring).
    Uses lens_hints, epistemic, family_id and query for differentiated text.
    Still INFERRED by design until full HERMENEUT contract.
    """
    base_epistemic = atom.epistemic or "INFERRED"
    family = atom.family_id
    hints = atom.lens_hints or {}

    historical_text = (
        f"Retrieved from {family} tradition. "
        f"Reflects documented witnesses; dating and attribution per source metadata. "
        f"Epistemic: {base_epistemic}."
    )
    if hints.get("historical"):
        historical_text = f"Historical lens prioritized per source hints. {historical_text}"

    symbolic_text = (
        f"Lexical match for '{query[:50]}' in {family}. "
        f"Symbolic readings are interpretive overlays on the cited text."
    )
    if hints.get("symbolic"):
        symbolic_text = f"Symbolic lens active per source. {symbolic_text}"

    operational_text = (
        "Returns historical/textual context only — "
        "no practice instructions, efficacy scores, or summon UX. "
        f"Operational structure from {family} records."
    )
    if hints.get("operational"):
        operational_text = f"Operational arrangement noted in source. {operational_text}"

    return {
        "historical": {"text": historical_text, "epistemic": "INFERRED"},
        "symbolic": {"text": symbolic_text, "epistemic": "INFERRED"},
        "operational": {"text": operational_text, "epistemic": "INFERRED"},
    }


def build_packet(
    query: str,
    ranked: Iterable[tuple[Atom, float]],
    *,
    query_tokens: Sequence[str] | None = None,
) -> dict[str, Any]:
    tokens = list(query_tokens) if query_tokens is not None else tokenize(query)
    hits: list[dict[str, Any]] = []
    synthesis = None  # per-packet or first-hit based for now

    for atom, _score in ranked:
        hit = {
            "atom_id": atom.atom_id,
            "family_id": atom.family_id,
            "excerpt": _excerpt(atom.text, tokens),
            "license": atom.license,
            "epistemic": atom.epistemic,
        }
        if atom.source_url:
            hit["source_url"] = atom.source_url
        if atom.content_hash:
            hit["content_hash"] = atom.content_hash
        hits.append(hit)
        if synthesis is None:
            synthesis = _build_lens_synthesis(atom, query)

    if synthesis is None:
        synthesis = {
            "historical": dict(_SYNTHESIS_STUBS["historical"]),
            "symbolic": dict(_SYNTHESIS_STUBS["symbolic"]),
            "operational": dict(_SYNTHESIS_STUBS["operational"]),
        }

    # Minimal receipt for provenance (closes deviation; can be extended by callers)
    receipts = [{"type": "lexical-retrieve", "epistemic": "INFERRED"}]

    return {
        "query": query,
        "hits": hits,
        "synthesis": synthesis,
        "efficacy": None,
        "epistemic": "INFERRED",
        "receipts": receipts,
    }


def retrieve(
    query: str,
    *,
    k: int = 5,
    family: str | None = None,
    corpus_path: Path | None = None,
) -> dict[str, Any]:
    """Load corpus, rank, and return an athanor.packet.v0 dict (efficacy always null)."""
    if not query or not query.strip():
        raise ValueError("query must be non-empty")
    q_tokens = tokenize(query)
    if not q_tokens:
        raise ValueError("query must contain at least one searchable token (alphanumeric)")
    atoms = load_atoms(corpus_path)
    ranked = rank_atoms(query, atoms, k=k, family=family)
    return build_packet(query, ranked, query_tokens=q_tokens)
