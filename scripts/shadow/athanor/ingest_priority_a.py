#!/usr/bin/env python3
"""ATHANOR-INGEST Priority A harvest — thin PD families via Crawl4AI + static mirror.

Local SoT only. No Firecrawl, no Wave 3b harvest, no Enochian flood,
no HF upload, no git-commit of atoms.
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
    "archive.sacred-texts.com",  # classic static mirror of sacred-texts
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
SLEEP_SEC = 2.1  # ≥2s between requests per host
MIN_PROSE = 400
MIN_ATOM = 400
MAX_ATOM = 2200
MAX_PAGE_CHARS = 120_000
FAMILY_SOFT_CAP = 55  # prefer 40–80; 7 families * 55 => each ≤~14% of NEW (<25%)
BALANCE_FRAC = 0.25  # no family > 25% of NEW atoms
HOST_FAIL_SKIP = 2

RUN_TS = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
RUN_ID = f"ingest-priority-a-{RUN_TS}-{uuid.uuid4().hex[:8]}"
TS_FILE = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

# Fetch via classic mirror; store canonical sacred-texts.com source_url.
MIRROR_HOST = "https://archive.sacred-texts.com"
CANON_HOST = "https://sacred-texts.com"

# ---------------------------------------------------------------------------
# Priority A seed plan (quality PD; skip Enochian; no Wave 3b)
# ---------------------------------------------------------------------------
PLAN: list[dict[str, Any]] = [
    # --- alchemy_spirit (spirit/process; NOT emerald/lab tablet) ---
    {
        "family_id": "alchemy_spirit",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "text",
        "urls": [
            f"{MIRROR_HOST}/alc/harcanum.htm",
            f"{MIRROR_HOST}/alc/goldtrac.htm",
            f"{MIRROR_HOST}/alc/eudoxus.htm",
            f"{MIRROR_HOST}/alc/freher.htm",
            f"{MIRROR_HOST}/alc/mirror.htm",
            f"{MIRROR_HOST}/alc/turba.htm",
            f"{MIRROR_HOST}/alc/turba2.htm",
            f"{MIRROR_HOST}/alc/emerglor.htm",
            f"{MIRROR_HOST}/alc/catena1.htm",
            f"{MIRROR_HOST}/alc/paracel1.htm",
            f"{MIRROR_HOST}/alc/paracel2.htm",
            f"{MIRROR_HOST}/alc/paracel3.htm",
            f"{MIRROR_HOST}/alc/coelum.htm",
            f"{MIRROR_HOST}/alc/tschoudy.htm",
            f"{MIRROR_HOST}/alc/maryprof.htm",
            f"{MIRROR_HOST}/alc/cc/cc09.htm",
            f"{MIRROR_HOST}/alc/cc/cc10.htm",
            f"{MIRROR_HOST}/alc/cc/cc12.htm",
            f"{MIRROR_HOST}/alc/cc/cc16.htm",
            f"{MIRROR_HOST}/alc/cc/cc20.htm",
            f"{MIRROR_HOST}/alc/cc/cc22.htm",  # Ripley Bosom Book
            f"{MIRROR_HOST}/alc/hm1/hm104.htm",
            f"{MIRROR_HOST}/alc/hm1/hm106.htm",
            f"{MIRROR_HOST}/alc/hm1/hm110.htm",
            f"{MIRROR_HOST}/alc/hm1/hm113.htm",
            f"{MIRROR_HOST}/alc/arr/arr13.htm",
            f"{MIRROR_HOST}/alc/arr/arr14.htm",
            f"{MIRROR_HOST}/alc/arr/arr15.htm",
        ],
        "soft_cap": FAMILY_SOFT_CAP,
    },
    # --- solomonic (Greater Key historical; not goetia summon UX) ---
    {
        "family_id": "solomonic",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "text",
        "urls": [
            f"{MIRROR_HOST}/grim/kos/kos03.htm",
            f"{MIRROR_HOST}/grim/kos/kos04.htm",
            f"{MIRROR_HOST}/grim/kos/kos05.htm",
            f"{MIRROR_HOST}/grim/kos/kos06.htm",
            f"{MIRROR_HOST}/grim/kos/kos07.htm",
            f"{MIRROR_HOST}/grim/kos/kos08.htm",
            f"{MIRROR_HOST}/grim/kos/kos09.htm",
            f"{MIRROR_HOST}/grim/kos/kos10.htm",
            f"{MIRROR_HOST}/grim/kos/kos13.htm",
            f"{MIRROR_HOST}/grim/kos/kos23.htm",
            f"{MIRROR_HOST}/grim/kos/kos36.htm",
            f"{MIRROR_HOST}/grim/kos/kos37.htm",
            f"{MIRROR_HOST}/grim/kos/kos38.htm",
            f"{MIRROR_HOST}/grim/kos/kos39.htm",
            f"{MIRROR_HOST}/grim/kos/kos40.htm",
            f"{MIRROR_HOST}/grim/kos/kos41.htm",
            f"{MIRROR_HOST}/grim/kos/kos42.htm",
            f"{MIRROR_HOST}/grim/kos/kos43.htm",
            f"{MIRROR_HOST}/grim/kos/kos44.htm",
            f"{MIRROR_HOST}/grim/kos/kos45.htm",
            f"{MIRROR_HOST}/grim/bcm/bcm13.htm",  # BCM section on Key of Solomon
        ],
        "soft_cap": FAMILY_SOFT_CAP,
    },
    # --- grimoire_other (Heptameron/Arbatel via BCM; Moses; Magus; Abramelin hist) ---
    {
        "family_id": "grimoire_other",
        "license": "public-domain",
        "reception_layer": "historical_commentary",
        "type": "text",
        "urls": [
            f"{MIRROR_HOST}/grim/bcm/bcm08.htm",  # Arbatel
            f"{MIRROR_HOST}/grim/bcm/bcm09.htm",
            f"{MIRROR_HOST}/grim/bcm/bcm18.htm",  # Heptameron
            f"{MIRROR_HOST}/grim/bcm/bcm19.htm",  # Abramelin summary
            f"{MIRROR_HOST}/grim/bcm/bcm05.htm",
            f"{MIRROR_HOST}/grim/bcm/bcm06.htm",
            f"{MIRROR_HOST}/grim/bcm/bcm12.htm",
            f"{MIRROR_HOST}/grim/moses6/m600.htm",
            f"{MIRROR_HOST}/grim/moses6/m601.htm",
            f"{MIRROR_HOST}/grim/moses6/m602.htm",
            f"{MIRROR_HOST}/grim/moses6/m603.htm",
            f"{MIRROR_HOST}/grim/moses7/m701.htm",
            f"{MIRROR_HOST}/grim/moses7/m702.htm",
            f"{MIRROR_HOST}/grim/moses7/m706.htm",
            f"{MIRROR_HOST}/grim/moses7/m707.htm",
            f"{MIRROR_HOST}/grim/moses7/m713.htm",
            f"{MIRROR_HOST}/grim/moses7/m716.htm",
            f"{MIRROR_HOST}/grim/magus/ma105.htm",
            f"{MIRROR_HOST}/grim/magus/ma106.htm",
            f"{MIRROR_HOST}/grim/magus/ma107.htm",
            f"{MIRROR_HOST}/grim/magus/ma123.htm",
            f"{MIRROR_HOST}/grim/abr/abr002.htm",
            f"{MIRROR_HOST}/grim/abr/abr006.htm",
            f"{MIRROR_HOST}/grim/abr/abr007.htm",
            f"{MIRROR_HOST}/grim/abr/abr020.htm",
            f"{MIRROR_HOST}/grim/abr/abr021.htm",
            f"{MIRROR_HOST}/grim/abr/abr023.htm",
        ],
        "soft_cap": FAMILY_SOFT_CAP,
    },
    # --- tarot_history (Waite Pictorial Key PD 1911; Papus TOB history ch) ---
    {
        "family_id": "tarot_history",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "text",
        "urls": [
            f"{MIRROR_HOST}/tarot/pkt/pktintr.htm",
            f"{MIRROR_HOST}/tarot/pkt/pkt0101.htm",
            f"{MIRROR_HOST}/tarot/pkt/pkt0102.htm",
            f"{MIRROR_HOST}/tarot/pkt/pkt0103.htm",
            f"{MIRROR_HOST}/tarot/pkt/pkt0104.htm",
            f"{MIRROR_HOST}/tarot/pkt/pkt0201.htm",
            f"{MIRROR_HOST}/tarot/pkt/pkt0202.htm",
            f"{MIRROR_HOST}/tarot/pkt/pktar01.htm",
            f"{MIRROR_HOST}/tarot/pkt/pktar02.htm",
            f"{MIRROR_HOST}/tarot/pkt/pktar03.htm",
            f"{MIRROR_HOST}/tarot/pkt/pktar10.htm",
            f"{MIRROR_HOST}/tarot/pkt/pktar15.htm",
            f"{MIRROR_HOST}/tarot/pkt/pktar19.htm",
            f"{MIRROR_HOST}/tarot/pkt/pktar21.htm",
            f"{MIRROR_HOST}/tarot/tob/tob03.htm",
            f"{MIRROR_HOST}/tarot/tob/tob11.htm",
            f"{MIRROR_HOST}/tarot/mathers/mtar01.htm",
            f"{MIRROR_HOST}/tarot/mathers/mtar02.htm",
            f"{MIRROR_HOST}/tarot/mathers/mtar06.htm",
            # Gutenberg Waite Pictorial Key full HTML (PD-US)
            "https://www.gutenberg.org/files/13415/13415-h/13415-h.htm",
        ],
        "soft_cap": FAMILY_SOFT_CAP,
        "gutenberg_segment": {
            "https://www.gutenberg.org/files/13415/13415-h/13415-h.htm": (8000, 90000),
        },
    },
    # --- mystery_cults (Mithra / Eleusis PD) ---
    {
        "family_id": "mystery_cults",
        "license": "public-domain",
        "reception_layer": "historical_commentary",
        "type": "text",
        "urls": [
            f"{MIRROR_HOST}/cla/mom/mom04.htm",
            f"{MIRROR_HOST}/cla/mom/mom05.htm",
            f"{MIRROR_HOST}/cla/mom/mom06.htm",
            f"{MIRROR_HOST}/cla/mom/mom07.htm",
            f"{MIRROR_HOST}/cla/mom/mom08.htm",
            f"{MIRROR_HOST}/cla/mom/mom09.htm",
            f"{MIRROR_HOST}/cla/mom/mom10.htm",
            f"{MIRROR_HOST}/cla/ebm/ebm04.htm",
            f"{MIRROR_HOST}/cla/ebm/ebm05.htm",
            f"{MIRROR_HOST}/cla/ebm/ebm06.htm",
            f"{MIRROR_HOST}/cla/ebm/ebm08.htm",
            f"{MIRROR_HOST}/cla/ebm/ebm09.htm",
        ],
        "soft_cap": FAMILY_SOFT_CAP,
    },
    # --- kabbalah_pd deepen ---
    {
        "family_id": "kabbalah_pd",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "text",
        "urls": [
            f"{MIRROR_HOST}/jud/sy/sy01.htm",
            f"{MIRROR_HOST}/jud/sy/sy02.htm",
            f"{MIRROR_HOST}/jud/sy/sy03.htm",
            f"{MIRROR_HOST}/jud/sy/sy04.htm",
            f"{MIRROR_HOST}/jud/sy/sy05.htm",
            f"{MIRROR_HOST}/jud/sy/sy06.htm",
            f"{MIRROR_HOST}/jud/sy/sy07.htm",
            f"{MIRROR_HOST}/jud/sy/sy08.htm",
            f"{MIRROR_HOST}/jud/cab/cab03.htm",
            f"{MIRROR_HOST}/jud/cab/cab04.htm",
            f"{MIRROR_HOST}/jud/cab/cab05.htm",
            f"{MIRROR_HOST}/jud/cab/cab07.htm",
            f"{MIRROR_HOST}/jud/jm/jm06.htm",
            f"{MIRROR_HOST}/jud/jm/jm09.htm",
            f"{MIRROR_HOST}/jud/jm/jm10.htm",
            f"{MIRROR_HOST}/jud/jm/jm11.htm",
            f"{MIRROR_HOST}/jud/jm/jm12.htm",
            f"{MIRROR_HOST}/jud/yetzirah.htm",
        ],
        "soft_cap": FAMILY_SOFT_CAP,
    },
    # --- runes_eddic deepen (skip already-thin index; prefer poems) ---
    {
        "family_id": "runes_eddic",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "text",
        "urls": [
            f"{MIRROR_HOST}/neu/poe/poe03.htm",  # Voluspo
            f"{MIRROR_HOST}/neu/poe/poe04.htm",  # Hovamol / Havamal
            f"{MIRROR_HOST}/neu/poe/poe05.htm",
            f"{MIRROR_HOST}/neu/poe/poe06.htm",
            f"{MIRROR_HOST}/neu/poe/poe10.htm",
            f"{MIRROR_HOST}/neu/poe/poe11.htm",
            f"{MIRROR_HOST}/neu/poe/poe12.htm",
            f"{MIRROR_HOST}/neu/poe/poe13.htm",
            f"{MIRROR_HOST}/neu/pre/pre02.htm",
            f"{MIRROR_HOST}/neu/pre/pre03.htm",
            f"{MIRROR_HOST}/neu/pre/pre04.htm",  # Gylfaginning (large)
            f"{MIRROR_HOST}/neu/onp/onp02.htm",
            f"{MIRROR_HOST}/neu/onp/onp03.htm",
            f"{MIRROR_HOST}/neu/onp/onp14.htm",
            f"{MIRROR_HOST}/neu/onp/onp18.htm",
        ],
        "soft_cap": FAMILY_SOFT_CAP,
    },
]

# Priority B light correspondence seeds (only if A yields enough)
PRIORITY_B: list[dict[str, Any]] = [
    {
        "family_id": "solomonic",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "table",
        "urls": [
            f"{MIRROR_HOST}/grim/kos/kos07.htm",  # days/hours/planets — may dupe
        ],
        "soft_cap": 8,
        "force_type": "correspondence",
    },
]

WAVE3B_PROPOSALS = [
    {"family_id": "thelema_pd", "note": "PROPOSAL ONLY — do not harvest this run"},
    {"family_id": "wicca_hist", "note": "PROPOSAL ONLY — do not harvest this run"},
]

HOLD_STATIC = [
    {"url_pattern": "sacred-texts.com/book/", "reason": "HOLD Rowe/Achadian modern /book/ essays"},
    {"family_id": "enochian", "reason": "HOLD — skip Enochian this run (prefer no flood)"},
]


def host_ok(url: str) -> bool:
    try:
        h = (urlparse(url).hostname or "").lower()
        if h in ALLOW_HOSTS:
            return True
        # allow *.sacred-texts.com
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
    """Store canonical sacred-texts.com URL when fetched from archive mirror."""
    u = normalize_url(url)
    p = urlparse(u)
    host = (p.hostname or "").lower()
    if host == "archive.sacred-texts.com":
        return f"{CANON_HOST}{p.path}"
    return u


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def atom_id_for(family_id: str, chash: str) -> str:
    # Match existing corpus style (16-hex prefix of sha256)
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




def load_existing_source_urls() -> set[str]:
    urls: set[str] = set()
    if not ATOMS_PATH.exists():
        return urls
    with ATOMS_PATH.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            u = obj.get("source_url")
            if u:
                urls.add(normalize_url(u))
                # also accept mirror form
                if "sacred-texts.com" in u:
                    urls.add(u.replace("https://sacred-texts.com", "https://archive.sacred-texts.com"))
                    urls.add(u.replace("https://www.sacred-texts.com", "https://archive.sacred-texts.com"))
    return urls


def count_priority_a_new() -> dict[str, int]:
    """Count atoms already written by Priority A ingest runs (session soft-cap credit)."""
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
            if hr.startswith("ingest-priority-a-"):
                fid = obj.get("family_id")
                if fid:
                    c[fid] += 1
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


def html_to_text(raw: str) -> str:
    if not raw:
        return ""
    # drop script/style
    raw = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", raw)
    raw = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", raw)
    raw = re.sub(r"(?is)<!--.*?-->", " ", raw)
    # headings / breaks -> newlines
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
        r"(?i)^buy (it here|the internet|disk)",
        r"(?i)^wisdom is priceless",
        r"(?i)^see site copyrights",
        r"(?i)^powered by",
        r"(?i)^search$",
        r"(?i)^faq$",
        r"(?i)^contact$",
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
            # likely breadcrumb crumbs
            if s.count(" ") < 4:
                continue
        out.append(line)
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def prepare_text(raw_md_or_html: str, is_html: bool) -> str:
    """Chrome-strip BEFORE length checks / store."""
    if is_html:
        text = html_to_text(raw_md_or_html)
    else:
        text = raw_md_or_html or ""
    text = clean_nav_lines(text)
    text = strip_chrome(text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def is_chrome_only(text: str) -> bool:
    if not text or len(text) < MIN_PROSE:
        return True
    # SPA leftover signals
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


def chunk_paragraphs(text: str, min_c: int = MIN_ATOM, max_c: int = MAX_ATOM) -> list[str]:
    if not text or len(text) < MIN_PROSE:
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
        if len(buf) >= min_c or (not chunks and len(buf) >= MIN_PROSE):
            chunks.append(buf)
        elif chunks:
            if len(chunks[-1]) + 2 + len(buf) <= max_c + 400:
                chunks[-1] = chunks[-1] + "\n\n" + buf
            else:
                chunks.append(buf)
    return chunks


def lens_for(family_id: str, typ: str) -> dict:
    base = {"historical": True, "symbolic": True, "operational": False}
    if typ in ("table", "correspondence"):
        base["symbolic"] = True
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
                _robots_cache[host] = None  # fail-open if robots unreachable
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
        return {"ok": True, "url": url, "error": None, "status": status, "body": body, "is_html": not bool(md)}
    except Exception as e:
        return {"ok": False, "url": url, "error": str(e), "status": None, "body": "", "is_html": False}


def balance_allows(by_family_new: dict[str, int], family: str) -> bool:
    """Soft balance during harvest.

    Soft-caps are sized so equal fill stays under 25%. Still block a family
    that would exceed BALANCE_FRAC once NEW mass is meaningful (>=40).
    """
    total_new = sum(by_family_new.values())
    if total_new <= 0:
        return True
    projected = by_family_new.get(family, 0) + 1
    if total_new + 1 < 40:
        return True
    return (projected / (total_new + 1)) <= (BALANCE_FRAC + 0.001)


async def main() -> None:
    before = family_counts()
    before_total = sum(before.values())
    existing = load_existing_hashes()
    prior_pa = count_priority_a_new()
    existing_urls = load_existing_source_urls()
    print(f"run_id={RUN_ID} existing_hashes={len(existing)} before_total={before_total}")
    print("before_by_family=", dict(before))
    print("prior_priority_a_new=", dict(prior_pa))
    print("HAS_CRAWL4AI=", HAS_CRAWL4AI)

    urls_attempted: list[dict] = []
    failures: list[dict] = []
    holds: list[dict] = list(HOLD_STATIC)
    atoms_written = 0
    atoms_skipped_dupe = 0
    by_family: dict[str, int] = defaultdict(int)
    # Seed soft-cap counters with prior Priority A session writes
    for fid, n in prior_pa.items():
        by_family[fid] = n
    sample_ids: list[str] = []
    pages_ok = 0
    pages_fail = 0
    host_fail_streak: dict[str, int] = defaultdict(int)
    skipped_hosts: set[str] = set()
    license_notes: list[str] = []

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
        jobs = list(PLAN)
        # Priority B only after Priority A has produced solid mass
        priority_b_armed = False

        for job in jobs:
            family = job["family_id"]
            if family == "enochian":
                holds.append({"family_id": family, "reason": "skip Enochian this run"})
                continue
            license_ = job["license"]
            if license_ not in {"public-domain", "pd-us", "cc0", "cc-by"}:
                holds.append({"family_id": family, "reason": f"unclear license {license_} — skip"})
                continue
            reception = job.get("reception_layer")
            typ = job.get("type") or "text"
            soft_cap = int(job.get("soft_cap") or FAMILY_SOFT_CAP)
            print(f"\n=== {family} (soft_cap={soft_cap}) ===")
            license_notes.append(f"{family}: stamped license={license_} (INFERRED PD edition claim; sacred-texts/Gutenberg hosts)")

            raw_urls = [normalize_url(u) for u in (job.get("urls") or [])]
            # Prefer URLs not yet in corpus so continue-pass reaches new chapters first
            unseen = [u for u in raw_urls if canon_source_url(u) not in existing_urls and u not in existing_urls]
            seen = [u for u in raw_urls if u not in unseen]
            ordered_urls = unseen + seen
            for url in ordered_urls:
                url = normalize_url(url)
                if by_family[family] >= soft_cap:
                    print(f"  soft_cap reached for {family}")
                    break
                if not balance_allows(by_family, family):
                    print(f"  balance rule: pause {family} (>{BALANCE_FRAC:.0%} of NEW)")
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
                # HOLD modern /book/ essays
                if "/book/" in urlparse(url).path and "sacred-texts.com" in host:
                    holds.append({"url": url, "reason": "HOLD Rowe/Achadian modern /book/ essays"})
                    continue
                path_l = urlparse(url).path.lower()
                if any(path_l.endswith(ext) for ext in (".pdf", ".epub", ".zip", ".djvu", ".mp3", ".mobi", ".gz")):
                    failures.append({"url": url, "error": "skipped binary extension"})
                    pages_fail += 1
                    continue

                print(f"  fetch {url}")
                # Prefer urllib for archive.sacred-texts.com / gutenberg files (static);
                # crawl4ai used for SPA-ish hosts when urllib body looks chrome-thin.
                use_c4a = False
                result = fetch_urllib(url)
                mode = "urllib"
                if result["ok"]:
                    preview = prepare_text(result["body"], result.get("is_html", True))
                    if is_chrome_only(preview) and crawler is not None:
                        use_c4a = True
                elif crawler is not None and result.get("status") != 404:
                    use_c4a = True

                if use_c4a:
                    result = await fetch_crawl4ai(crawler, url)
                    mode = "crawl4ai"

                urls_attempted.append({
                    "url": url,
                    "source_url_canon": canon_source_url(url),
                    "family_id": family,
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
                    # 404 → FAILED, never invent excerpt
                    if status == 404 or "404" in str(err):
                        host_fail_streak[host] = 0  # 404 is not a host outage
                    else:
                        host_fail_streak[host] += 1
                        if host_fail_streak[host] >= HOST_FAIL_SKIP:
                            skipped_hosts.add(host)
                            print(f"    skip host {host} after {HOST_FAIL_SKIP} consecutive failures")
                    continue

                host_fail_streak[host] = 0
                pages_ok += 1
                body = result.get("body") or ""
                # optional gutenberg segment window
                seg = (job.get("gutenberg_segment") or {}).get(url)
                if seg:
                    start, end = seg
                    body = body[start:end]
                    print(f"    gutenberg segment[{start}:{end}] -> {len(body)}")

                text = prepare_text(body, result.get("is_html", True))
                if len(text) > MAX_PAGE_CHARS:
                    text = text[:MAX_PAGE_CHARS]
                    print("    truncated to 120k")

                if is_chrome_only(text):
                    holds.append({"url": url, "reason": "DROP SPA/chrome-only after strip_chrome"})
                    print(f"    DROP chrome-only ({len(text)} chars)")
                    continue

                chunks = chunk_paragraphs(text)
                print(f"    prose={len(text)} -> {len(chunks)} chunks")
                atom_type = job.get("force_type") or typ

                for chunk in chunks:
                    if by_family[family] >= soft_cap:
                        break
                    if not balance_allows(by_family, family):
                        break
                    # chrome strip already applied to full text; re-strip chunk for safety
                    chunk = strip_chrome(chunk).strip()
                    if len(chunk) < MIN_PROSE:
                        continue
                    ch = content_hash(chunk)
                    if ch in existing:
                        atoms_skipped_dupe += 1
                        continue
                    aid = atom_id_for(family, ch)
                    atom = {
                        "atom_id": aid,
                        "family_id": family,
                        "type": atom_type,
                        "text": chunk,
                        "license": license_,
                        "source_url": canon_source_url(url),
                        "epistemic": "INFERRED",
                        "content_hash": ch,
                        "lens_hints": lens_for(family, atom_type),
                        "harvest_run": RUN_ID,
                    }
                    if reception:
                        atom["reception_layer"] = reception
                    with ATOMS_PATH.open("a") as f:
                        f.write(json.dumps(atom, ensure_ascii=False) + "\n")
                    existing.add(ch)
                    atoms_written += 1
                    by_family[family] += 1
                    if len(sample_ids) < 8:
                        sample_ids.append(aid)

            if atoms_written >= 200 and not priority_b_armed:
                priority_b_armed = True
                # append light Priority B once A has enough
                for b in PRIORITY_B:
                    jobs.append(b)
                print("\n-- Priority B armed (light correspondence) --")

    finally:
        if crawler_cm is not None:
            await crawler_cm.__aexit__(None, None, None)

    after = family_counts()
    after_total = sum(after.values())

    # Net-new this process only (by_family was seeded with prior_pa)
    by_family_this = {k: max(0, by_family.get(k, 0) - prior_pa.get(k, 0)) for k in set(by_family) | set(prior_pa)}
    by_family_this = {k: v for k, v in by_family_this.items() if v > 0}
    session_new = {k: by_family.get(k, 0) for k in set(by_family) | set(prior_pa) if by_family.get(k, 0) > 0}

    # Wave 3b proposals only
    for p in WAVE3B_PROPOSALS:
        holds.append(p)

    # Balance check across full Priority A session
    session_total = sum(session_new.values()) or 1
    balance_violations = []
    for fid, n in session_new.items():
        share = n / session_total
        if share > BALANCE_FRAC + 0.001:
            balance_violations.append({"family_id": fid, "n": n, "share": round(share, 4)})

    receipt = {
        "run_id": RUN_ID,
        "job_type": "harvest",
        "engine": "crawl4ai",
        "engine_version": "0.9.3",
        "fetch_notes": "urllib for archive.sacred-texts.com static PD HTML + Gutenberg files; crawl4ai fallback when chrome-thin",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "allowlist": sorted(ALLOW_HOSTS),
        "user_agent": UA,
        "rate_limit_sec": SLEEP_SEC,
        "epistemic": "INFERRED",
        "pages_ok": pages_ok,
        "pages_fail": pages_fail,
        "atoms_written": atoms_written,
        "atoms_skipped_dupe": atoms_skipped_dupe,
        "by_family_new": by_family_this,
        "by_family_session_priority_a": session_new,
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
        "atoms_path": str(ATOMS_PATH),
        "sample_atom_ids": sample_ids,
        "skipped_hosts": sorted(skipped_hosts),
        "proposals": {
            "KEEP": [f for f, n in by_family.items() if n > 0],
            "HOLD": [h for h in holds],
            "DROP": [h for h in holds if "DROP" in str(h.get("reason", ""))],
        },
    }
    receipt_path = RECEIPTS_DIR / f"{RUN_ID}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False))

    # Scoreboard
    priority_a = [
        "alchemy_spirit", "grimoire_other", "tarot_history", "mystery_cults",
        "solomonic", "kabbalah_pd", "runes_eddic",
    ]
    lines = [
        "# Ingest Priority A scoreboard",
        "",
        f"- run_id: `{RUN_ID}`",
        "- job_type: harvest",
        "- engine: crawl4ai 0.9.3 (+ urllib static mirror)",
        f"- timestamp_utc: {receipt['timestamp_utc']}",
        f"- pages_ok: **{pages_ok}**",
        f"- pages_fail: **{pages_fail}**",
        f"- atoms_written: **{atoms_written}**",
        f"- atoms_skipped_dupe: {atoms_skipped_dupe}",
        f"- before_total: {before_total} → after_total: {after_total}",
        f"- receipt: `{receipt_path}`",
        f"- atoms: `{ATOMS_PATH}`",
        f"- UA: `{UA}`",
        "- chrome_strip: yes (athanor.chrome.strip_chrome before length/store)",
        "- no Firecrawl; no Wave 3b harvest; no Enochian flood",
        "",
        "## Priority A family deltas",
        "",
        "| family_id | before | after | delta |",
        "|---|---:|---:|---:|",
    ]
    for fid in priority_a:
        b = before.get(fid, 0)
        a = after.get(fid, 0)
        lines.append(f"| `{fid}` | {b} | {a} | {a - b:+d} |")
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
    total_new = sum(by_family_this.values()) or 1
    for fid, n in sorted(by_family_this.items(), key=lambda x: (-x[1], x[0])):
        pct = 100.0 * n / total_new
        flag = " ⚠" if pct > 25.01 else ""
        lines.append(f"- `{fid}`: {n} ({pct:.1f}% of NEW){flag}")
    lines.append("")
    lines.append("## HOLD")
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
    lines.append("- HOLD: Wave 3b families (thelema_pd, wicca_hist); Rowe/Achadian /book/; chrome-only drops")
    lines.append("- DROP: SPA chrome-only after strip; HTTP 404 pages (FAILED, no invented excerpt)")
    lines.append("")
    scoreboard_path = SCOREBOARD_DIR / f"ingest-priority-a-{TS_FILE}.md"
    scoreboard_path.write_text("\n".join(lines) + "\n")

    summary = {
        "pages_ok": pages_ok,
        "pages_fail": pages_fail,
        "atoms_written": atoms_written,
        "atoms_skipped_dupe": atoms_skipped_dupe,
        "before_total": before_total,
        "after_total": after_total,
        "by_family_new": by_family_this,
        "by_family_session": session_new,
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
