#!/usr/bin/env python3
"""ATHANOR-INGEST Priority B — PD correspondence / table atoms for unbind.

Local SoT only. No Firecrawl, no Wave 3b harvest, no Enochian ritual flood,
no HF upload, no git-commit of atoms. Types: table | correspondence only.
"""
from __future__ import annotations

import asyncio
import hashlib
import html as html_lib
import json
import re
import sys
import uuid
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

sys.path.insert(0, "/workspace/Athanor/src")
from athanor.chrome import strip_chrome  # noqa: E402

try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
    HAS_CRAWL4AI = True
except Exception:
    HAS_CRAWL4AI = False

HOME = Path.home()
# Unreviewed harvests are candidates, never automatically admitted to retrieval.
ATOMS_PATH = HOME / ".athanor" / "staging" / "legacy-harvest" / "candidates.jsonl"
RECEIPTS_DIR = HOME / ".athanor" / "receipts"
SCOREBOARD_DIR = Path("/workspace/athanor-harvest")
ATOMS_PATH.parent.mkdir(parents=True, exist_ok=True)
RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
SCOREBOARD_DIR.mkdir(parents=True, exist_ok=True)

ALLOW_HOSTS = {
    "sacred-texts.com",
    "www.sacred-texts.com",
    "archive.sacred-texts.com",
    "archive.org",
    "www.gutenberg.org",
    "www.perseus.tufts.edu",
    "cdli.ucla.edu",
    "oracc.museum.upenn.edu",
    "www.metmuseum.org",
    "www.britishmuseum.org",
    "wellcomecollection.org",
}

UA = "AthanorCorpusBot/0.2"
SLEEP_SEC = 2.1
MIN_PROSE = 400
MIN_ATOM = 400
MIN_TABLE_ATOM = 180  # real table structure may be shorter
MAX_ATOM = 2200
MAX_PAGE_CHARS = 120_000
FAMILY_SOFT_CAP = 22  # ~5–6 families × 22 ≈ under 120; each ≤25% of NEW
BALANCE_FRAC = 0.25
HOST_FAIL_SKIP = 2
TARGET_MIN = 40
TARGET_MAX = 120

RUN_TS = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
RUN_ID = f"ingest-priority-b-{RUN_TS}-{uuid.uuid4().hex[:8]}"
TS_FILE = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

MIRROR_HOST = "https://archive.sacred-texts.com"
CANON_HOST = "https://sacred-texts.com"

# ---------------------------------------------------------------------------
# Priority B plan — correspondence / table families (existing family_ids only)
# ---------------------------------------------------------------------------
def _ich_urls(start: int, end: int) -> list[str]:
    return [f"{MIRROR_HOST}/ich/ic{n:02d}.htm" for n in range(start, end + 1)]


PLAN: list[dict[str, Any]] = [
    # --- kabbalah_pd: letter attributions + sephirah/path doctrines ---
    {
        "family_id": "kabbalah_pd",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "correspondence",
        "correspondence_kind": "letter-watchtower",  # hebrew letter tables (non-Enochian)
        "urls": [
            f"{MIRROR_HOST}/jud/sy/sy02.htm",
            f"{MIRROR_HOST}/jud/sy/sy03.htm",
            f"{MIRROR_HOST}/jud/sy/sy04.htm",
            f"{MIRROR_HOST}/jud/sy/sy05.htm",
            f"{MIRROR_HOST}/jud/sy/sy06.htm",
            f"{MIRROR_HOST}/jud/sy/sy07.htm",
            f"{MIRROR_HOST}/jud/sy/sy08.htm",
            f"{MIRROR_HOST}/jud/yetzirah.htm",
        ],
        "soft_cap": 18,
        "prefer_tables": True,
        "keywords": [
            "letter", "letters", "sephir", "path", "mother", "double",
            "element", "planet", "zodiac", "hebrew", "aleph", "beth",
        ],
    },
    {
        "family_id": "kabbalah_pd",
        "license": "public-domain",
        "reception_layer": "historical_commentary",
        "type": "correspondence",
        "correspondence_kind": "sephirah-path",
        "urls": [
            f"{MIRROR_HOST}/jud/cab/cab04.htm",
            f"{MIRROR_HOST}/jud/cab/cab07.htm",
            f"{MIRROR_HOST}/jud/tku/tku07.htm",
            f"{MIRROR_HOST}/jud/tku/tku08.htm",
            f"{MIRROR_HOST}/jud/jm/jm09.htm",
            f"{MIRROR_HOST}/jud/jm/jm10.htm",
            f"{MIRROR_HOST}/jud/jm/jm11.htm",
        ],
        "soft_cap": 18,  # shared with prior kabbalah job via session counter
        "prefer_tables": True,
        "keywords": [
            "sephir", "sephiroth", "path", "emanation", "kether", "chokmah",
            "binah", "chesed", "geburah", "tiphareth", "netzach", "hod",
            "yesod", "malkuth", "tree",
        ],
    },
    # --- iching_daoist: hexagram judgments (Legge PD) ---
    {
        "family_id": "iching_daoist",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "correspondence",
        "correspondence_kind": "hexagram-judgment",
        "urls": _ich_urls(1, 32) + [
            f"{MIRROR_HOST}/ich/icintr02.htm",  # lineal figures explanation
            f"{MIRROR_HOST}/ich/icap5.htm",  # remarks on trigrams
        ],
        "soft_cap": 22,
        "one_atom_per_page": True,
        "prefer_tables": False,
        "keywords": ["hexagram", "khien", "judgment", "nine", "six", "trigram"],
    },
    {
        "family_id": "iching_daoist",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "correspondence",
        "correspondence_kind": "hexagram-judgment",
        "urls": _ich_urls(33, 64),
        "soft_cap": 22,
        "one_atom_per_page": True,
        "prefer_tables": False,
        "keywords": ["hexagram", "judgment", "nine", "six"],
    },
    # --- hermetic / Magus (Agrippa-derived Barrett) planet-metal + scales + elements ---
    {
        "family_id": "hermetic",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "table",
        "correspondence_kind": "planet-metal",
        "urls": [
            f"{MIRROR_HOST}/grim/magus/ma123.htm",  # four elements
            f"{MIRROR_HOST}/grim/magus/ma124.htm",
            f"{MIRROR_HOST}/grim/magus/ma125.htm",
            f"{MIRROR_HOST}/grim/magus/ma132.htm",  # perfumes to seven planets
            f"{MIRROR_HOST}/grim/magus/ma138.htm",  # scale of unity
            f"{MIRROR_HOST}/grim/magus/ma139.htm",
            f"{MIRROR_HOST}/grim/magus/ma140.htm",
            f"{MIRROR_HOST}/grim/magus/ma141.htm",  # scale of four / elements
            f"{MIRROR_HOST}/grim/magus/ma144.htm",  # scale of seven / planets
            f"{MIRROR_HOST}/grim/magus/ma147.htm",  # scale of ten
            f"{MIRROR_HOST}/grim/magus/ma148.htm",  # cabalistical scale 11–12
            f"{MIRROR_HOST}/grim/magus/ma149.htm",  # hebrew/chaldean notes
            f"{MIRROR_HOST}/grim/magus/ma150.htm",  # magic tables of planets
        ],
        "soft_cap": 20,
        "prefer_tables": True,
        "force_type_if_table": "table",
        "keywords": [
            "planet", "metal", "gold", "silver", "iron", "copper", "tin",
            "lead", "mercury", "scale", "element", "fire", "water", "air",
            "earth", "saturn", "jupiter", "mars", "venus", "sun", "moon",
        ],
    },
    # --- astrology_west: planet-day-hour + mansions ---
    {
        "family_id": "astrology_west",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "correspondence",
        "correspondence_kind": "planet-day-hour",
        "urls": [
            f"{MIRROR_HOST}/grim/kos/kos07.htm",  # days/hours/planets
            f"{MIRROR_HOST}/grim/magus/ma151.htm",
            f"{MIRROR_HOST}/grim/magus/ma152.htm",
            f"{MIRROR_HOST}/grim/magus/ma153.htm",
            f"{MIRROR_HOST}/grim/magus/ma154.htm",
            f"{MIRROR_HOST}/grim/magus/ma155.htm",  # 28 mansions
            f"{MIRROR_HOST}/astro/ptb/ptb06.htm",
            f"{MIRROR_HOST}/astro/ptb/ptb07.htm",
            f"{MIRROR_HOST}/astro/ptb/ptb08.htm",
            f"{MIRROR_HOST}/astro/ptb/ptb31.htm",
        ],
        "soft_cap": 18,
        "prefer_tables": True,
        "keywords": [
            "hour", "hours", "day", "planet", "saturn", "jupiter", "mars",
            "sun", "venus", "mercury", "moon", "mansion", "influence",
        ],
    },
    # --- hermetic element-direction via Magus / related ---
    {
        "family_id": "hermetic",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "correspondence",
        "correspondence_kind": "element-direction",
        "urls": [
            f"{MIRROR_HOST}/grim/magus/ma126.htm",
            f"{MIRROR_HOST}/grim/magus/ma127.htm",
            f"{MIRROR_HOST}/grim/magus/ma128.htm",
            f"{MIRROR_HOST}/grim/magus/ma129.htm",
            f"{MIRROR_HOST}/grim/magus/ma130.htm",
            f"{MIRROR_HOST}/grim/magus/ma131.htm",
        ],
        "soft_cap": 20,
        "prefer_tables": True,
        "keywords": [
            "element", "fire", "water", "air", "earth", "east", "west",
            "north", "south", "quarter", "direction", "wind",
        ],
    },
    # --- tarot_history: Waite suit/element historical ---
    {
        "family_id": "tarot_history",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "correspondence",
        "correspondence_kind": "tarot-suit-element",
        "urls": [
            f"{MIRROR_HOST}/tarot/pkt/pkt0101.htm",
            f"{MIRROR_HOST}/tarot/pkt/pkt0102.htm",
            f"{MIRROR_HOST}/tarot/pkt/pkt0103.htm",
            f"{MIRROR_HOST}/tarot/pkt/pkt0104.htm",
            f"{MIRROR_HOST}/tarot/pkt/pkt0201.htm",
            f"{MIRROR_HOST}/tarot/pkt/pkt0202.htm",
            f"{MIRROR_HOST}/tarot/mathers/mtar01.htm",
            f"{MIRROR_HOST}/tarot/mathers/mtar02.htm",
            f"{MIRROR_HOST}/tarot/mathers/mtar06.htm",
        ],
        "soft_cap": 16,
        "prefer_tables": True,
        "keywords": [
            "suit", "wands", "cups", "swords", "pentacles", "element",
            "fire", "water", "air", "earth", "trumps", "minor", "court",
        ],
    },
    # --- alchemy_spirit: planet-metal process correspondences ---
    {
        "family_id": "alchemy_spirit",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "correspondence",
        "correspondence_kind": "planet-metal",
        "urls": [
            f"{MIRROR_HOST}/alc/paracel1.htm",
            f"{MIRROR_HOST}/alc/paracel2.htm",
            f"{MIRROR_HOST}/alc/paracel3.htm",
            f"{MIRROR_HOST}/alc/coelum.htm",
            f"{MIRROR_HOST}/alc/hm1/hm104.htm",
            f"{MIRROR_HOST}/alc/hm1/hm106.htm",
        ],
        "soft_cap": 14,
        "prefer_tables": True,
        "keywords": [
            "metal", "gold", "silver", "iron", "copper", "tin", "lead",
            "mercury", "planet", "saturn", "jupiter", "mars", "sol", "luna",
            "venus", "antimony", "sulphur", "salt",
        ],
    },
]

HOLD_STATIC = [
    {"url_pattern": "sacred-texts.com/book/", "reason": "HOLD Rowe/Achadian modern /book/ essays"},
    {"family_id": "enochian", "reason": "HOLD — prefer Hebrew/kabbalah letter tables over Enochian watchtower ritual; skip Enochian this run"},
    {"family_id": "runes_eddic", "reason": "HOLD — no clean PD rune correspondence table in allowlisted set this run (poem text already Priority A)"},
    {"family_id": "thelema_pd", "note": "PROPOSAL ONLY — Wave 3b; do not harvest"},
    {"family_id": "wicca_hist", "note": "PROPOSAL ONLY — Wave 3b; do not harvest"},
]


def host_ok(url: str) -> bool:
    try:
        h = (urlparse(url).hostname or "").lower()
        if h in ALLOW_HOSTS:
            return True
        if h.endswith(".sacred-texts.com") or h == "sacred-texts.com":
            return True
        return False
    except Exception:
        return False


def normalize_url(url: str) -> str:
    u = url.strip()
    if "#" in u:
        u = u.split("#", 1)[0]
    return u


def canon_source_url(url: str) -> str:
    u = normalize_url(url)
    p = urlparse(u)
    host = (p.hostname or "").lower()
    if host == "archive.sacred-texts.com":
        return f"{CANON_HOST}{p.path}"
    return u


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def atom_id_for(family_id: str, chash: str) -> str:
    return f"{family_id}:{chash[:16]}"


def family_counts() -> Counter:
    c: Counter = Counter()
    if ATOMS_PATH.exists():
        with ATOMS_PATH.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    c[obj.get("family_id", "?")] += 1
                except json.JSONDecodeError:
                    continue
    return c


def load_existing_hashes() -> set[str]:
    hashes: set[str] = set()
    if ATOMS_PATH.exists():
        with ATOMS_PATH.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if "content_hash" in obj:
                        hashes.add(obj["content_hash"])
                except json.JSONDecodeError:
                    continue
    return hashes


def count_priority_b_new() -> dict[str, int]:
    c: dict[str, int] = defaultdict(int)
    if not ATOMS_PATH.exists():
        return c
    with ATOMS_PATH.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            hr = str(obj.get("harvest_run") or "")
            if hr.startswith("ingest-priority-b-"):
                fid = obj.get("family_id")
                if fid:
                    c[fid] += 1
    return c


def html_to_text(raw: str) -> str:
    if not raw:
        return ""
    raw = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", raw)
    raw = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", raw)
    raw = re.sub(r"(?is)<!--.*?-->", " ", raw)
    raw = re.sub(r"(?i)<br\s*/?>", "\n", raw)
    raw = re.sub(r"(?i)</p>", "\n\n", raw)
    raw = re.sub(r"(?i)</(h[1-6]|div|tr|li)>", "\n", raw)
    raw = re.sub(r"<[^>]+>", " ", raw)
    text = html_lib.unescape(raw)
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_nav_lines(text: str) -> str:
    if not text:
        return ""
    skip = [
        r"(?i)^sacred.?texts$",
        r"(?i)^home$",
        r"(?i)^index$",
        r"(?i)^(next|previous|contents|start reading)\b",
        r"(?i)^buy (it here|the internet|disk|this book)",
        r"(?i)^wisdom is priceless",
        r"(?i)^see site copyrights",
        r"(?i)^powered by",
        r"(?i)^search$",
        r"(?i)^faq$",
        r"(?i)^contact$",
        r"(?i)^grimoires$",
        r"(?i)^judaism$",
        r"(?i)^sky lore$",
        r"(?i)^tarot$",
        r"(?i)^tarot reading$",
    ]
    out = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            out.append("")
            continue
        if any(re.match(p, s) for p in skip):
            continue
        if len(s) < 40 and re.search(r"(?i)\b(next|previous|home|index|faq)\b", s) and "http" not in s:
            if s.count(" ") < 4:
                continue
        out.append(line)
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def prepare_text(raw_md_or_html: str, is_html: bool) -> str:
    if is_html:
        text = html_to_text(raw_md_or_html)
    else:
        text = raw_md_or_html or ""
    text = clean_nav_lines(text)
    text = strip_chrome(text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def is_chrome_only(text: str) -> bool:
    if not text or len(text) < 200:
        return True
    low = text.lower()
    chrome_hits = sum(
        1
        for p in (
            "toggle sidebar",
            "buy usb drive",
            "close navigation",
            "own the wisdom of the ages",
            "sign in access your account",
        )
        if p in low
    )
    if chrome_hits >= 2 and len(text) < 1200:
        return True
    return False


def extract_html_tables(raw_html: str) -> list[tuple[str, int, int]]:
    """Return list of (tsv_text, nrows, ncols) for real data tables (skip nav)."""
    if not raw_html:
        return []
    out: list[tuple[str, int, int]] = []
    for m in re.finditer(r"(?is)<table\b[^>]*>(.*?)</table>", raw_html):
        block = m.group(0)
        rows = re.findall(r"(?is)<tr\b[^>]*>(.*?)</tr>", block)
        if len(rows) < 2:
            continue
        parsed_rows: list[list[str]] = []
        for row in rows:
            cells = re.findall(r"(?is)<t[hd]\b[^>]*>(.*?)</t[hd]>", row)
            cleaned = []
            for c in cells:
                c = re.sub(r"(?is)<br\s*/?>", " / ", c)
                c = re.sub(r"<[^>]+>", " ", c)
                c = html_lib.unescape(c)
                c = re.sub(r"\s+", " ", c).strip()
                cleaned.append(c)
            if any(cleaned):
                parsed_rows.append(cleaned)
        if len(parsed_rows) < 2:
            continue
        ncols = max(len(r) for r in parsed_rows)
        # skip skinny chrome tables
        joined = " ".join(" ".join(r) for r in parsed_rows).lower()
        if any(x in joined for x in ("toggle sidebar", "buy usb", "own the wisdom")):
            continue
        if ncols < 2 and len(parsed_rows) < 4:
            continue
        # pad
        lines = []
        for r in parsed_rows:
            while len(r) < ncols:
                r.append("")
            lines.append(" | ".join(r))
        tsv = "\n".join(lines).strip()
        tsv = strip_chrome(tsv).strip()
        if len(tsv) < 40:
            continue
        out.append((tsv, len(parsed_rows), ncols))
    return out


def looks_like_table_text(text: str) -> bool:
    if not text:
        return False
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if len(lines) < 3:
        return False
    pipe_rows = sum(1 for ln in lines if ln.count("|") >= 2)
    tab_rows = sum(1 for ln in lines if "\t" in ln)
    colon_rows = sum(1 for ln in lines if re.search(r"\w\s*[:—–-]\s*\w", ln))
    return pipe_rows >= 3 or tab_rows >= 3 or (colon_rows >= 5 and len(lines) >= 5)


def keyword_density(text: str, keywords: list[str]) -> float:
    if not text or not keywords:
        return 0.0
    low = text.lower()
    hits = sum(1 for k in keywords if k.lower() in low)
    return hits / max(1, len(keywords))


def chunk_paragraphs(text: str, min_c: int = MIN_ATOM, max_c: int = MAX_ATOM) -> list[str]:
    if not text or len(text) < min(min_c, MIN_PROSE):
        # allow short only if caller already validated table structure
        if not text:
            return []
    paras = re.split(r"\n\s*\n", text)
    paras = [p.strip() for p in paras if p.strip()]
    chunks: list[str] = []
    buf = ""
    for p in paras:
        pieces = [p]
        if len(p) > max_c:
            pieces = []
            sent_parts = re.split(r"(?<=[.!?])\s+", p)
            cur = ""
            for s in sent_parts:
                if cur and len(cur) + 1 + len(s) > max_c:
                    pieces.append(cur)
                    cur = s
                else:
                    cur = (cur + " " + s).strip() if cur else s
            if cur:
                pieces.append(cur)
        for piece in pieces:
            if not buf:
                buf = piece
            elif len(buf) + 2 + len(piece) <= max_c:
                buf = buf + "\n\n" + piece
            else:
                if len(buf) >= min_c:
                    chunks.append(buf)
                    buf = piece
                else:
                    if len(buf) + 2 + len(piece) <= max_c + 400:
                        buf = buf + "\n\n" + piece
                        chunks.append(buf)
                        buf = ""
                    else:
                        chunks.append(buf)
                        buf = piece
    if buf:
        if len(buf) >= min_c or (not chunks and len(buf) >= min(min_c, 200)):
            chunks.append(buf)
        elif chunks:
            if len(chunks[-1]) + 2 + len(buf) <= max_c + 400:
                chunks[-1] = chunks[-1] + "\n\n" + buf
            else:
                chunks.append(buf)
    return chunks


def page_as_single_atom(text: str, max_c: int = MAX_ATOM) -> list[str]:
    """For hexagram pages: keep judgment block as one atom (trim chrome/page nums)."""
    text = re.sub(r"(?m)^p\.\s*\d+\s*$", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        return []
    if len(text) <= max_c:
        return [text]
    # Prefer first max_c at paragraph boundary
    cut = text[:max_c]
    sp = cut.rfind("\n\n")
    if sp > max_c // 2:
        cut = cut[:sp]
    return [cut.strip()]


def lens_for(family_id: str, typ: str, kind: str | None) -> dict:
    base: dict[str, Any] = {"historical": True, "symbolic": True, "operational": False}
    if typ in ("table", "correspondence"):
        base["symbolic"] = True
    if kind:
        base["correspondence_kind"] = kind
    return base


_robots_cache: dict[str, RobotFileParser | None] = {}


def robots_allowed(url: str) -> bool:
    try:
        p = urlparse(url)
        host = (p.hostname or "").lower()
        if host not in _robots_cache:
            rp = RobotFileParser()
            robots_url = f"{p.scheme}://{p.hostname}/robots.txt"
            try:
                req = urllib.request.Request(robots_url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    rp.parse(resp.read().decode("utf-8", "replace").splitlines())
                _robots_cache[host] = rp
            except Exception:
                _robots_cache[host] = None
        rp = _robots_cache[host]
        if rp is None:
            return True
        return rp.can_fetch(UA, url)
    except Exception:
        return True


def fetch_urllib(url: str, timeout: int = 90) -> dict[str, Any]:
    if not host_ok(url):
        return {"ok": False, "url": url, "error": "host not allowlisted", "status": None, "body": "", "is_html": True}
    if not robots_allowed(url):
        return {"ok": False, "url": url, "error": "robots.txt disallow", "status": None, "body": "", "is_html": True}
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = getattr(resp, "status", 200)
            raw = resp.read()
            ctype = (resp.headers.get("Content-Type") or "").lower()
            text = None
            for enc in ("utf-8", "latin-1", "cp1252"):
                try:
                    text = raw.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            if text is None:
                text = raw.decode("utf-8", errors="replace")
            if status == 404:
                return {"ok": False, "url": url, "error": "HTTP 404", "status": 404, "body": "", "is_html": True}
            is_html = "html" in ctype or text.lstrip().lower().startswith("<!doctype") or "<html" in text[:500].lower()
            return {"ok": True, "url": url, "error": None, "status": status, "body": text, "is_html": is_html}
    except urllib.error.HTTPError as e:
        return {"ok": False, "url": url, "error": f"HTTP {e.code}", "status": e.code, "body": "", "is_html": True}
    except Exception as e:
        return {"ok": False, "url": url, "error": str(e), "status": None, "body": "", "is_html": True}


async def fetch_crawl4ai(crawler: Any, url: str) -> dict[str, Any]:
    if not host_ok(url):
        return {"ok": False, "url": url, "error": "host not allowlisted", "status": None, "body": "", "is_html": False}
    if not robots_allowed(url):
        return {"ok": False, "url": url, "error": "robots.txt disallow", "status": None, "body": "", "is_html": False}
    cfg = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=10,
        exclude_external_links=False,
        page_timeout=60000,
        wait_until="domcontentloaded",
        user_agent=UA,
    )
    try:
        result = await crawler.arun(url=url, config=cfg)
        ok = bool(getattr(result, "success", False))
        status = getattr(result, "status_code", None)
        err = getattr(result, "error_message", None) or ""
        md = ""
        if getattr(result, "markdown", None):
            m = result.markdown
            if hasattr(m, "raw_markdown"):
                md = m.raw_markdown or ""
            elif isinstance(m, str):
                md = m
            else:
                md = str(m)
        html = getattr(result, "html", None) or ""
        if status == 404:
            return {"ok": False, "url": url, "error": "HTTP 404", "status": 404, "body": "", "is_html": False}
        if not ok:
            return {"ok": False, "url": url, "error": err or "crawl failed", "status": status, "body": md or html, "is_html": bool(html and not md)}
        body = md if md else html
        return {"ok": True, "url": url, "error": None, "status": status, "body": body, "is_html": not bool(md), "html": html}
    except Exception as e:
        return {"ok": False, "url": url, "error": str(e), "status": None, "body": "", "is_html": False}


def balance_allows(by_family_new: dict[str, int], family: str) -> bool:
    total_new = sum(by_family_new.values())
    if total_new <= 0:
        return True
    projected = by_family_new.get(family, 0) + 1
    if total_new + 1 < 24:
        return True
    return (projected / (total_new + 1)) <= (BALANCE_FRAC + 0.001)


def accept_chunk(chunk: str, is_table: bool, keywords: list[str], dens_min: float = 0.12) -> bool:
    chunk = chunk.strip()
    if not chunk:
        return False
    if is_table or looks_like_table_text(chunk):
        return len(chunk) >= MIN_TABLE_ATOM or (len(chunk) >= 80 and looks_like_table_text(chunk))
    if len(chunk) < MIN_ATOM:
        return False
    # correspondence prose must show topic signal
    dens = keyword_density(chunk, keywords) if keywords else 1.0
    return dens >= dens_min


async def main() -> None:
    before = family_counts()
    before_total = sum(before.values())
    existing = load_existing_hashes()
    prior_pb = count_priority_b_new()
    print(f"run_id={RUN_ID} existing_hashes={len(existing)} before_total={before_total}")
    print("before_by_family=", dict(before))
    print("prior_priority_b_new=", dict(prior_pb))
    print("HAS_CRAWL4AI=", HAS_CRAWL4AI)

    urls_attempted: list[dict] = []
    failures: list[dict] = []
    holds: list[dict] = list(HOLD_STATIC)
    atoms_written = 0
    atoms_skipped_dupe = 0
    atoms_skipped_quality = 0
    by_family: dict[str, int] = defaultdict(int)
    by_kind: dict[str, int] = defaultdict(int)
    for fid, n in prior_pb.items():
        by_family[fid] = n
    sample_ids: list[str] = []
    pages_ok = 0
    pages_fail = 0
    host_fail_streak: dict[str, int] = defaultdict(int)
    skipped_hosts: set[str] = set()
    license_notes: list[str] = []
    type_counts: Counter = Counter()

    crawler = None
    crawler_cm = None
    if HAS_CRAWL4AI:
        try:
            browser_cfg = BrowserConfig(headless=True, verbose=False)
        except TypeError:
            browser_cfg = BrowserConfig(headless=True)
        crawler_cm = AsyncWebCrawler(config=browser_cfg)
        crawler = await crawler_cm.__aenter__()

    try:
        for job in PLAN:
            if atoms_written >= TARGET_MAX:
                holds.append({"reason": f"TARGET_MAX {TARGET_MAX} reached; stop harvest"})
                break
            family = job["family_id"]
            if family == "enochian":
                holds.append({"family_id": family, "reason": "skip Enochian this run"})
                continue
            license_ = job["license"]
            if license_ not in {"public-domain", "pd-us", "cc0", "cc-by"}:
                holds.append({"family_id": family, "reason": f"unclear license {license_} — skip"})
                continue
            reception = job.get("reception_layer")
            typ = job.get("type") or "correspondence"
            kind = job.get("correspondence_kind")
            soft_cap = int(job.get("soft_cap") or FAMILY_SOFT_CAP)
            keywords = list(job.get("keywords") or [])
            prefer_tables = bool(job.get("prefer_tables"))
            one_per = bool(job.get("one_atom_per_page"))
            print(f"\n=== {family} kind={kind} type={typ} soft_cap={soft_cap} ===")
            license_notes.append(
                f"{family}/{kind}: stamped license={license_} (INFERRED PD edition; sacred-texts mirror)"
            )

            for url in [normalize_url(u) for u in (job.get("urls") or [])]:
                if atoms_written >= TARGET_MAX:
                    break
                if by_family[family] >= soft_cap:
                    print(f"  soft_cap reached for {family}")
                    break
                if not balance_allows(by_family, family):
                    print(f"  balance rule: pause {family}")
                    holds.append({"family_id": family, "reason": "balance pause >25% of NEW atoms"})
                    break

                host = (urlparse(url).hostname or "").lower()
                if host in skipped_hosts:
                    failures.append({"url": url, "error": "host skipped after consecutive failures", "status": None})
                    pages_fail += 1
                    continue
                if not host_ok(url):
                    failures.append({"url": url, "error": "host not allowlisted"})
                    pages_fail += 1
                    continue
                if "/book/" in urlparse(url).path and "sacred-texts.com" in host:
                    holds.append({"url": url, "reason": "HOLD Rowe/Achadian modern /book/ essays"})
                    continue
                path_l = urlparse(url).path.lower()
                if any(path_l.endswith(ext) for ext in (".pdf", ".epub", ".zip", ".djvu", ".mp3", ".mobi", ".gz")):
                    failures.append({"url": url, "error": "skipped binary extension"})
                    pages_fail += 1
                    continue

                print(f"  fetch {url}")
                result = fetch_urllib(url)
                mode = "urllib"
                html_body = result.get("body") or "" if result.get("is_html") else ""
                if result["ok"]:
                    preview = prepare_text(result["body"], result.get("is_html", True))
                    if is_chrome_only(preview) and crawler is not None:
                        result = await fetch_crawl4ai(crawler, url)
                        mode = "crawl4ai"
                        html_body = result.get("html") or (result.get("body") if result.get("is_html") else "") or ""
                elif crawler is not None and result.get("status") != 404:
                    result = await fetch_crawl4ai(crawler, url)
                    mode = "crawl4ai"
                    html_body = result.get("html") or ""

                if result.get("is_html") and not html_body:
                    html_body = result.get("body") or ""

                urls_attempted.append({
                    "url": url,
                    "source_url_canon": canon_source_url(url),
                    "family_id": family,
                    "kind": kind,
                    "ok": result["ok"],
                    "status": result.get("status"),
                    "error": result.get("error"),
                    "mode": mode,
                })
                await asyncio.sleep(SLEEP_SEC)

                if not result["ok"]:
                    pages_fail += 1
                    err = result.get("error") or "fail"
                    status = result.get("status")
                    failures.append({"url": url, "error": err, "status": status})
                    print(f"    FAILED: {err}")
                    if status == 404 or "404" in str(err):
                        host_fail_streak[host] = 0
                    else:
                        host_fail_streak[host] += 1
                        if host_fail_streak[host] >= HOST_FAIL_SKIP:
                            skipped_hosts.add(host)
                            print(f"    skip host {host} after {HOST_FAIL_SKIP} consecutive failures")
                    continue

                host_fail_streak[host] = 0
                pages_ok += 1
                body = result.get("body") or ""
                text = prepare_text(body, result.get("is_html", True))
                if len(text) > MAX_PAGE_CHARS:
                    text = text[:MAX_PAGE_CHARS]
                    print("    truncated to 120k")

                if is_chrome_only(text) and len(text) < MIN_PROSE:
                    holds.append({"url": url, "reason": "DROP SPA/chrome-only after strip_chrome"})
                    print(f"    DROP chrome-only ({len(text)} chars)")
                    continue

                candidate_chunks: list[tuple[str, str]] = []  # (text, type)

                # 1) HTML tables first when prefer_tables
                if prefer_tables and html_body:
                    for tsv, nrows, ncols in extract_html_tables(html_body):
                        header = f"[table {nrows}x{ncols} | {kind or 'correspondence'}]\n"
                        payload = header + tsv
                        if len(payload) < MIN_TABLE_ATOM and nrows >= 3 and ncols >= 2:
                            # pad with surrounding prose context if short
                            payload = header + tsv + "\n\n" + text[: max(0, MIN_TABLE_ATOM - len(payload) + 80)]
                        atom_typ = job.get("force_type_if_table") or "table"
                        candidate_chunks.append((payload.strip(), atom_typ))

                # 2) page-level or paragraph chunks
                if one_per:
                    for ch in page_as_single_atom(text):
                        candidate_chunks.append((ch, typ))
                else:
                    # denser filter: keep paragraphs with keyword hits
                    dens = keyword_density(text, keywords)
                    min_c = MIN_ATOM
                    if dens < 0.08 and not prefer_tables:
                        print(f"    skip low keyword density={dens:.2f}")
                        atoms_skipped_quality += 1
                        continue
                    for ch in chunk_paragraphs(text, min_c=min_c):
                        candidate_chunks.append((ch, typ))

                print(f"    prose={len(text)} candidates={len(candidate_chunks)}")
                wrote_page = 0
                for chunk, atom_type in candidate_chunks:
                    if by_family[family] >= soft_cap or atoms_written >= TARGET_MAX:
                        break
                    if not balance_allows(by_family, family):
                        break
                    chunk = strip_chrome(chunk).strip()
                    is_tab = atom_type == "table" or looks_like_table_text(chunk) or chunk.startswith("[table ")
                    if not accept_chunk(chunk, is_tab, keywords, dens_min=0.10 if not one_per else 0.05):
                        atoms_skipped_quality += 1
                        continue
                    # clamp
                    if len(chunk) > MAX_ATOM + 400:
                        chunk = chunk[: MAX_ATOM + 400]
                    chash = content_hash(chunk)
                    if chash in existing:
                        atoms_skipped_dupe += 1
                        continue
                    aid = atom_id_for(family, chash)
                    atom = {
                        "atom_id": aid,
                        "family_id": family,
                        "type": atom_type if atom_type in ("table", "correspondence") else "correspondence",
                        "text": chunk,
                        "license": license_,
                        "source_url": canon_source_url(url),
                        "epistemic": "INFERRED",
                        "content_hash": chash,
                        "lens_hints": lens_for(family, atom_type, kind),
                        "harvest_run": RUN_ID,
                    }
                    if reception:
                        atom["reception_layer"] = reception
                    with ATOMS_PATH.open("a") as f:
                        f.write(json.dumps(atom, ensure_ascii=False) + "\n")
                    existing.add(chash)
                    atoms_written += 1
                    by_family[family] += 1
                    by_kind[kind or "?"] += 1
                    type_counts[atom["type"]] += 1
                    wrote_page += 1
                    if len(sample_ids) < 12:
                        sample_ids.append(aid)
                    if one_per and wrote_page >= 1:
                        break
                print(f"    wrote={wrote_page}")

    finally:
        if crawler_cm is not None:
            await crawler_cm.__aexit__(None, None, None)

    after = family_counts()
    after_total = sum(after.values())
    by_family_this = {
        k: max(0, by_family.get(k, 0) - prior_pb.get(k, 0))
        for k in set(by_family) | set(prior_pb)
    }
    by_family_this = {k: v for k, v in by_family_this.items() if v > 0}

    session_total = sum(by_family_this.values()) or 1
    balance_violations = []
    for fid, n in by_family_this.items():
        share = n / session_total
        if share > BALANCE_FRAC + 0.001:
            balance_violations.append({"family_id": fid, "n": n, "share": round(share, 4)})

    if atoms_written < TARGET_MIN:
        holds.append({
            "reason": f"below TARGET_MIN {TARGET_MIN} (got {atoms_written}) — quality gate preferred over flood",
        })

    receipt = {
        "run_id": RUN_ID,
        "job_type": "harvest",
        "priority": "B",
        "engine": "crawl4ai",
        "engine_version": "0.9.3",
        "fetch_notes": "urllib for archive.sacred-texts.com static PD HTML; crawl4ai fallback when chrome-thin",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "allowlist": sorted(ALLOW_HOSTS),
        "user_agent": UA,
        "rate_limit_sec": SLEEP_SEC,
        "epistemic": "INFERRED",
        "atom_types": ["table", "correspondence"],
        "type_counts": dict(type_counts),
        "by_correspondence_kind": dict(by_kind),
        "pages_ok": pages_ok,
        "pages_fail": pages_fail,
        "atoms_written": atoms_written,
        "atoms_skipped_dupe": atoms_skipped_dupe,
        "atoms_skipped_quality": atoms_skipped_quality,
        "by_family_new": by_family_this,
        "balance_violations": balance_violations,
        "before_by_family": dict(before),
        "after_by_family": dict(after),
        "before_total": before_total,
        "after_total": after_total,
        "urls": urls_attempted,
        "FAILED": failures,
        "HOLD": holds,
        "license_notes": license_notes,
        "balance_rule": f"no family > {BALANCE_FRAC:.0%} of NEW",
        "chrome_strip": True,
        "no_firecrawl": True,
        "no_wave3b_harvest": True,
        "no_enochian_flood": True,
        "no_git_commit_atoms": True,
        "no_efficacy": True,
        "atoms_path": str(ATOMS_PATH),
        "backup_hint": "atoms.pre-ingest-b-*.jsonl",
        "sample_atom_ids": sample_ids,
        "skipped_hosts": sorted(skipped_hosts),
        "target_range": [TARGET_MIN, TARGET_MAX],
        "proposals": {
            "KEEP": sorted(by_family_this.keys()),
            "HOLD": [h for h in holds if "DROP" not in str(h.get("reason", ""))],
            "DROP": [h for h in holds if "DROP" in str(h.get("reason", ""))],
        },
    }
    receipt_path = RECEIPTS_DIR / f"{RUN_ID}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False))

    lines = [
        "# Ingest Priority B scoreboard — correspondence / table atoms",
        "",
        f"- run_id: `{RUN_ID}`",
        "- job_type: harvest | priority: B",
        "- engine: crawl4ai 0.9.3 (+ urllib static mirror)",
        f"- timestamp_utc: {receipt['timestamp_utc']}",
        f"- pages_ok: **{pages_ok}** | pages_fail: **{pages_fail}**",
        f"- atoms_written: **{atoms_written}** | dupes: {atoms_skipped_dupe} | quality_skips: {atoms_skipped_quality}",
        f"- before_total: **{before_total}** → after_total: **{after_total}**",
        f"- types: `{dict(type_counts)}`",
        f"- kinds: `{dict(by_kind)}`",
        f"- receipt: `{receipt_path}`",
        f"- atoms: `{ATOMS_PATH}`",
        f"- UA: `{UA}`",
        "- chrome_strip: yes | allowlist respected | no Firecrawl | no Wave 3b | no Enochian flood | no efficacy",
        "- balance: max family share of NEW checked (limit 25%)",
        "",
        "## Priority B family deltas",
        "",
        "| family_id | before | after | delta | % of NEW |",
        "|---|---:|---:|---:|---:|",
    ]
    total_new = sum(by_family_this.values()) or 1
    focus = [
        "kabbalah_pd", "iching_daoist", "hermetic", "astrology_west",
        "tarot_history", "alchemy_spirit", "runes_eddic", "enochian",
    ]
    for fid in focus:
        b = before.get(fid, 0)
        a = after.get(fid, 0)
        d = a - b
        pct = (100.0 * by_family_this.get(fid, 0) / total_new) if d else 0.0
        lines.append(f"| `{fid}` | {b} | {a} | {d:+d} | {pct:.1f}% |")
    lines.append("")
    lines.append("## All families (after)")
    lines.append("")
    lines.append("| family_id | before | after | delta |")
    lines.append("|---|---:|---:|---:|")
    all_fams = sorted(set(before) | set(after) | set(by_family), key=lambda x: (-after.get(x, 0), x))
    for fid in all_fams:
        b = before.get(fid, 0)
        a = after.get(fid, 0)
        lines.append(f"| `{fid}` | {b} | {a} | {a - b:+d} |")
    lines.append("")
    lines.append("## NEW atoms this run")
    lines.append("")
    for fid, n in sorted(by_family_this.items(), key=lambda x: (-x[1], x[0])):
        pct = 100.0 * n / total_new
        flag = " ⚠" if pct > 25.01 else ""
        lines.append(f"- `{fid}`: {n} ({pct:.1f}% of NEW){flag}")
    lines.append("")
    lines.append("## Correspondence kinds")
    lines.append("")
    for k, n in sorted(by_kind.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"- `{k}`: {n}")
    lines.append("")
    lines.append("## HOLD (with reason)")
    lines.append("")
    for h in holds:
        lines.append(f"- {json.dumps(h, ensure_ascii=False)}")
    lines.append("")
    lines.append("## FAILED")
    lines.append("")
    if not failures:
        lines.append("- (none)")
    else:
        for fail in failures[:80]:
            lines.append(f"- {fail.get('url')}: {fail.get('error')} (status={fail.get('status')})")
        if len(failures) > 80:
            lines.append(f"- … +{len(failures) - 80} more")
    lines.append("")
    lines.append("## INFERRED license notes")
    lines.append("")
    for n in license_notes:
        lines.append(f"- {n}")
    lines.append("")
    lines.append("## Sample atom_ids")
    lines.append("")
    for s in sample_ids:
        lines.append(f"- `{s}`")
    lines.append("")
    lines.append("## Propose (never GOLD)")
    lines.append("")
    lines.append(f"- KEEP: {sorted(by_family_this.keys())}")
    lines.append("- HOLD: Enochian watchtower ritual pages; runes_eddic (no clean table); Wave 3b; Rowe `/book/`")
    lines.append("- DROP: SPA chrome-only after strip; HTTP 404 (FAILED, no invented excerpt)")
    lines.append("")

    scoreboard_path = SCOREBOARD_DIR / f"ingest-priority-b-{TS_FILE}.md"
    scoreboard_path.write_text("\n".join(lines) + "\n")

    # also copy script into harvest dir for convenience
    try:
        import shutil
        shutil.copy2(Path(__file__), SCOREBOARD_DIR / "ingest_priority_b.py")
    except Exception:
        pass

    summary = {
        "pages_ok": pages_ok,
        "pages_fail": pages_fail,
        "atoms_written": atoms_written,
        "atoms_skipped_dupe": atoms_skipped_dupe,
        "atoms_skipped_quality": atoms_skipped_quality,
        "before_total": before_total,
        "after_total": after_total,
        "by_family_new": by_family_this,
        "by_kind": dict(by_kind),
        "type_counts": dict(type_counts),
        "balance_violations": balance_violations,
        "receipt": str(receipt_path),
        "scoreboard": str(scoreboard_path),
        "sample_ids": sample_ids,
        "failures": len(failures),
        "holds": len(holds),
    }
    print("\n==== DONE ====")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
