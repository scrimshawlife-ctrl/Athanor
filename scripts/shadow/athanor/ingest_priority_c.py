#!/usr/bin/env python3
"""ATHANOR-INGEST Priority C — islamic_occult_pd (Picatrix / Arabic occult-scientific PD).

Local SoT only. No Firecrawl, no Wave 3b, no Enochian, no HF upload, no git-commit
of atoms. Prefer PD historical commentary + period transmission witnesses.
"""
from __future__ import annotations

import asyncio
import hashlib
import html as html_lib
import json
import re
import shutil
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
CACHE_DIR = SCOREBOARD_DIR / "cache-c"
ATOMS_PATH.parent.mkdir(parents=True, exist_ok=True)
RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
SCOREBOARD_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

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
MIN_TABLE_ATOM = 180
MAX_ATOM = 2200
MAX_PAGE_CHARS = 120_000
FAMILY_SOFT_CAP = 85  # single-family Priority C; prefer 40–80 quality
TARGET_MIN = 40
TARGET_MAX = 80
HOST_FAIL_SKIP = 2

RUN_TS = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
RUN_ID = f"ingest-priority-c-{RUN_TS}-{uuid.uuid4().hex[:8]}"
TS_FILE = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
BACKUP_NAME = f"atoms.pre-ingest-c-{RUN_TS}.jsonl"

MIRROR_HOST = "https://archive.sacred-texts.com"
CANON_HOST = "https://sacred-texts.com"

# ---------------------------------------------------------------------------
# Priority C plan — islamic_occult_pd only
# ---------------------------------------------------------------------------
ISLAMIC_KW = [
    "picatrix", "arabic", "arab", "islam", "alkindi", "kindi", "albumasar",
    "abu ma", "thebit", "thabit", "harran", "sabian", "talisman", "image",
    "astral", "astrology", "occult", "rasis", "razi", "translator", "latin",
    "ghayat", "hakim", "majriti", "alfonso", "costa ben", "messahala",
    "ikhw", "brethren", "basra", "farabi", "avicen", "ibn sina", "hermes",
    "planet", "mansions", "suffumig", "necromanc", "magic", "science",
]

HOLD_STATIC = [
    {
        "url": "https://archive.org/details/goal-of-the-wise-english",
        "reason": "HOLD — 2022 Abdullah Hashem English Goal of the Wise (copyrighted modern)",
    },
    {
        "url": "https://archive.org/details/the-picatrix-the-goal-of-the-wise-by-hashem-atallah",
        "reason": "HOLD — Hashem Atallah modern English Picatrix translation (copyright-unclear/modern)",
    },
    {
        "url": "https://archive.org/details/christopher-warnock-the-complete-picatrix",
        "reason": "HOLD — Warnock/Greer modern Complete Picatrix (post-1928 copyright)",
    },
    {
        "url": "https://archive.org/details/picatrix_20190508",
        "reason": "HOLD — anonymous English picatrix upload; no PD year/creator; likely modern translation",
    },
    {
        "url": "https://archive.org/details/picatrix_202012",
        "reason": "HOLD — Alfonso X Picatrix concordance (Hispanic Seminary); stamped CC-BY-ND (not cc-by/pd) + modern editorial layer; OCR also unusable",
    },
    {
        "url": "https://archive.org/details/picatrix-ghayat-al-hakim-al-majriti",
        "reason": "HOLD — Arabic Ghayat al-Hakim upload; no clear PD edition year/license (may be Ritter or modern print)",
    },
    {
        "family_id": "enochian",
        "reason": "HOLD — out of Priority C scope",
    },
    {
        "note": "Wave 3b families — PROPOSAL ONLY; do not harvest",
        "family_ids": ["thelema_pd", "wicca_hist"],
    },
]

# Gutenberg chapter slices (local cache; previously fetched with UA)
GUTENBERG_JOBS: list[dict[str, Any]] = [
    {
        "family_id": "islamic_occult_pd",
        "license": "public-domain",
        "reception_layer": "historical_commentary",
        "type": "text",
        "correspondence_kind": "picatrix-reception",
        "source_url": "https://www.gutenberg.org/ebooks/67330",
        "local_path": str(CACHE_DIR / "pg67330.txt"),
        "chapter_start": "CHAPTER LXVI",
        "chapter_end": "CHAPTER LXVII",
        "label": "Thorndike 1923 vol2 ch66 Picatrix",
        "soft_cap": 18,
        "keywords": ISLAMIC_KW + ["picatrix", "alfonso", "astronomical images", "compilation"],
        "dens_min": 0.08,
    },
    {
        "family_id": "islamic_occult_pd",
        "license": "public-domain",
        "reception_layer": "historical_commentary",
        "type": "text",
        "correspondence_kind": "arabic-occult-science",
        "source_url": "https://www.gutenberg.org/ebooks/67792",
        "local_path": str(CACHE_DIR / "pg67792.txt"),
        "chapter_start": "CHAPTER XXVIII",
        "chapter_end": "CHAPTER XXIX",
        "label": "Thorndike 1923 vol1 ch28 Arabic occult science (Alkindi/Albumasar/Thebit/Rasis)",
        "soft_cap": 22,
        "keywords": ISLAMIC_KW,
        "dens_min": 0.10,
    },
    {
        "family_id": "islamic_occult_pd",
        "license": "public-domain",
        "reception_layer": "historical_commentary",
        "type": "text",
        "correspondence_kind": "arabic-astrology-transmission",
        "source_url": "https://www.gutenberg.org/ebooks/67792",
        "local_path": str(CACHE_DIR / "pg67792.txt"),
        "chapter_start": "CHAPTER XXX",
        "chapter_end": "CHAPTER XXXI",
        "label": "Thorndike 1923 vol1 ch30 Gerbert + Arabic astrology introduction",
        "soft_cap": 12,
        "keywords": ISLAMIC_KW + ["gerbert", "alchandrus", "arabic", "astrolabe", "astrology"],
        "dens_min": 0.05,
    },
    {
        "family_id": "islamic_occult_pd",
        "license": "public-domain",
        "reception_layer": "historical_commentary",
        "type": "text",
        "correspondence_kind": "arabic-astrology-transmission",
        "source_url": "https://www.gutenberg.org/ebooks/67330",
        "local_path": str(CACHE_DIR / "pg67330.txt"),
        "chapter_start": "CHAPTER XXXVIII",
        "chapter_end": "CHAPTER XXXIX",
        "label": "Thorndike 1923 vol2 ch38 12th-c translators of Arabic astrology",
        "soft_cap": 16,
        "keywords": ISLAMIC_KW + ["translator", "toledo", "plato of tivoli", "john of seville", "astrology"],
        "dens_min": 0.06,
        "max_chunks": 16,
    },
]

HTML_PLAN: list[dict[str, Any]] = [
    {
        "family_id": "islamic_occult_pd",
        "license": "public-domain",
        "reception_layer": "historical_commentary",
        "type": "text",
        "correspondence_kind": "arabic-philosophy-occult",
        "urls": [
            f"{MIRROR_HOST}/isl/hpi/hpi13.htm",  # Faithful Brethren of Basra
            f"{MIRROR_HOST}/isl/hpi/hpi14.htm",  # Kindi
            f"{MIRROR_HOST}/isl/hpi/hpi12.htm",  # Natural Philosophy
            f"{MIRROR_HOST}/isl/hpi/hpi07.htm",  # Greek Science (transmission context)
            f"{MIRROR_HOST}/isl/ath/ath06.htm",  # Translators
            f"{MIRROR_HOST}/isl/ath/ath04.htm",  # Arab Period
            f"{MIRROR_HOST}/isl/ath/ath08.htm",  # Eastern Philosophers
            f"{MIRROR_HOST}/isl/ath/ath03.htm",  # Syriac Hellenism
        ],
        "soft_cap": 20,
        "keywords": ISLAMIC_KW + ["brethren", "basra", "kindi", "philosophy", "science", "translator"],
        "dens_min": 0.08,
    },
    {
        "family_id": "islamic_occult_pd",
        "license": "public-domain",
        "reception_layer": "historical_commentary",
        "type": "correspondence",
        "correspondence_kind": "talisman-historical",
        "urls": [
            # Pavitt 1914 Book of Talismans — only chapters with Arab/Islamic historical notes
            f"{MIRROR_HOST}/sym/bot/bot04.htm",
            f"{MIRROR_HOST}/sym/bot/bot10.htm",
            f"{MIRROR_HOST}/sym/bot/bot11.htm",
            f"{MIRROR_HOST}/sym/bot/bot13.htm",
        ],
        "soft_cap": 10,
        "keywords": ["arab", "arabic", "islam", "talisman", "egypt", "persian", "magic", "amulet"],
        "dens_min": 0.12,
        "require_any": ["arab", "arabic", "islam", "persian", "egypt"],
    },
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


def html_to_text(raw: str) -> str:
    if not raw:
        return ""
    raw = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", raw)
    raw = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", raw)
    raw = re.sub(r"(?is)<!--.*?-->", " ", raw)
    raw = re.sub(r"(?i)<br\s*/?>", "\n", raw)
    raw = re.sub(r"(?i)</p>", "\n\n", raw)
    raw = re.sub(r"(?i)</div>", "\n", raw)
    raw = re.sub(r"(?i)</h[1-6]>", "\n\n", raw)
    raw = re.sub(r"(?i)</li>", "\n", raw)
    raw = re.sub(r"(?i)</tr>", "\n", raw)
    raw = re.sub(r"(?i)</t[dh]>", " | ", raw)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = html_lib.unescape(raw)
    raw = re.sub(r"[ \t]+", " ", raw)
    raw = re.sub(r"\n[ \t]+", "\n", raw)
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    return raw.strip()


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
        r"(?i)^islam$",
        r"(?i)^symbolism$",
        r"(?i)^project gutenberg",
        r"(?i)^the project gutenberg eBook",
        r"(?i)^this eBook is for the use of anyone",
        r"(?i)^\*\*\* START OF",
        r"(?i)^\*\*\* END OF",
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


def has_require_any(text: str, require_any: list[str] | None) -> bool:
    if not require_any:
        return True
    low = text.lower()
    return any(k.lower() in low for k in require_any)


def is_efficacy_frame(text: str) -> bool:
    """Skip operational summon/efficacy framing; keep historical access language."""
    low = text.lower()
    # Pure recipe/operational frames without historical distance
    bad = [
        r"(?i)\bsummon(?:s|ed|ing)?\s+(?:the\s+)?(?:spirit|demon|angel|jinn)",
        r"(?i)\bthis will cause\b",
        r"(?i)\bto make a woman love\b",
        r"(?i)\bsay this conjuration\b",
        r"(?i)\bguaranteed results\b",
    ]
    hits = sum(1 for p in bad if re.search(p, text))
    if hits >= 1 and "thorndike" not in low and "chapter" not in low and "manuscript" not in low:
        # If chunk is mostly imperative recipe without scholarly framing
        if not any(w in low for w in ("history", "medieval", "latin", "arabic", "author", "manuscript", "century")):
            return True
    return False


def chunk_paragraphs(text: str, min_c: int = MIN_ATOM, max_c: int = MAX_ATOM) -> list[str]:
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


def ensure_gutenberg_cache() -> list[dict]:
    """Fetch missing Gutenberg plaintexts into cache (UA + ≥2s)."""
    notes = []
    files = {
        CACHE_DIR / "pg67792.txt": "https://www.gutenberg.org/files/67792/67792-0.txt",
        CACHE_DIR / "pg67330.txt": "https://www.gutenberg.org/files/67330/67330-0.txt",
        CACHE_DIR / "pg69622.txt": "https://www.gutenberg.org/files/69622/69622-0.txt",
    }
    for path, url in files.items():
        if path.exists() and path.stat().st_size > 100_000:
            notes.append({"path": str(path), "status": "cached", "bytes": path.stat().st_size})
            continue
        print(f"fetch gutenberg {url}")
        res = fetch_urllib(url, timeout=120)
        import time as _t
        _t.sleep(SLEEP_SEC)
        if not res["ok"]:
            notes.append({"path": str(path), "status": "fail", "error": res.get("error")})
            continue
        path.write_text(res["body"], encoding="utf-8")
        notes.append({"path": str(path), "status": "downloaded", "bytes": len(res["body"])})
    return notes


def extract_chapter(text: str, start_marker: str, end_marker: str) -> str:
    # Prefer line-anchored CHAPTER headings
    start_re = re.compile(rf"(?m)^\s*{re.escape(start_marker)}\b")
    end_re = re.compile(rf"(?m)^\s*{re.escape(end_marker)}\b")
    sm = start_re.search(text)
    if not sm:
        # fallback substring
        idx = text.find(start_marker)
        if idx < 0:
            return ""
        start = idx
    else:
        start = sm.start()
    em = end_re.search(text, start + len(start_marker))
    end = em.start() if em else len(text)
    return text[start:end].strip()


def clean_thorndike_chapter(text: str) -> str:
    # Drop dense footnote-only trailing manuscript catalogs if they dominate — keep body
    text = re.sub(r"(?m)^\[Sidenote:\s*", "[", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Remove pure page-number lines
    text = re.sub(r"(?m)^\s*\d{1,4}\s*$", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def accept_chunk(
    chunk: str,
    is_table: bool,
    keywords: list[str],
    dens_min: float = 0.10,
    require_any: list[str] | None = None,
) -> bool:
    chunk = chunk.strip()
    if not chunk:
        return False
    if is_efficacy_frame(chunk):
        return False
    if not has_require_any(chunk, require_any):
        return False
    if is_table or looks_like_table_text(chunk):
        return len(chunk) >= MIN_TABLE_ATOM or (len(chunk) >= 80 and looks_like_table_text(chunk))
    if len(chunk) < MIN_ATOM:
        return False
    dens = keyword_density(chunk, keywords) if keywords else 1.0
    return dens >= dens_min


def backup_corpus() -> Path:
    dest = ATOMS_PATH.parent / BACKUP_NAME
    if ATOMS_PATH.exists():
        # Prefer keep existing backup from this run if already created externally
        if not dest.exists():
            shutil.copy2(ATOMS_PATH, dest)
    return dest


async def main() -> None:
    backup = backup_corpus()
    before = family_counts()
    before_total = sum(before.values())
    existing = load_existing_hashes()
    print(f"run_id={RUN_ID} existing_hashes={len(existing)} before_total={before_total}")
    print("before islamic_occult_pd=", before.get("islamic_occult_pd", 0))
    print("HAS_CRAWL4AI=", HAS_CRAWL4AI)
    print("backup=", backup)

    cache_notes = ensure_gutenberg_cache()
    print("cache_notes=", cache_notes)

    urls_attempted: list[dict] = []
    failures: list[dict] = []
    holds: list[dict] = list(HOLD_STATIC)
    atoms_written = 0
    atoms_skipped_dupe = 0
    atoms_skipped_quality = 0
    by_family: dict[str, int] = defaultdict(int)
    by_kind: dict[str, int] = defaultdict(int)
    sample_ids: list[str] = []
    pages_ok = 0
    pages_fail = 0
    host_fail_streak: dict[str, int] = defaultdict(int)
    skipped_hosts: set[str] = set()
    license_notes: list[str] = [
        "Thorndike, A History of Magic and Experimental Science vols 1–2 (1923): PD-US (pub. 1923 → PD 2019); Gutenberg 67792/67330 (INFERRED).",
        "Thorndike ch.66 Picatrix: historical commentary on Latin Picatrix tradition — used in lieu of copyrighted modern English translations (INFERRED).",
        "de Boer, History of Philosophy in Islam (1903 Eng.): public-domain sacred-texts (INFERRED).",
        "O'Leary, Arabic Thought and Its Place in History (1922): public-domain sacred-texts (INFERRED).",
        "Pavitt, Book of Talismans (1914): public-domain; only Arab/Islamic-historical leaves kept (INFERRED).",
        "Modern Picatrix English (Warnock/Greer, Atallah, Hashem 2022): HOLD copyright — not harvested.",
        "archive.org Alfonso X Picatrix concordance: HOLD CC-BY-ND + modern editorial; Arabic Ghayat upload: HOLD license-unclear.",
    ]
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
        # ---- Local Gutenberg chapter jobs ----
        for job in GUTENBERG_JOBS:
            if atoms_written >= TARGET_MAX:
                holds.append({"reason": f"TARGET_MAX {TARGET_MAX} reached; stop harvest"})
                break
            family = job["family_id"]
            if by_family[family] >= FAMILY_SOFT_CAP:
                break
            path = Path(job["local_path"])
            label = job.get("label") or path.name
            print(f"\n=== LOCAL {label} ===")
            if not path.exists():
                pages_fail += 1
                failures.append({"url": job["source_url"], "error": f"missing cache {path}", "status": None})
                continue
            raw = path.read_text(encoding="utf-8", errors="replace")
            chapter = extract_chapter(raw, job["chapter_start"], job["chapter_end"])
            urls_attempted.append({
                "url": job["source_url"],
                "source_url_canon": job["source_url"],
                "family_id": family,
                "kind": job.get("correspondence_kind"),
                "ok": bool(chapter),
                "status": 200 if chapter else None,
                "error": None if chapter else "chapter extract empty",
                "mode": "local-gutenberg",
                "label": label,
                "chapter_chars": len(chapter),
            })
            if not chapter or len(chapter) < MIN_PROSE:
                pages_fail += 1
                failures.append({"url": job["source_url"], "error": f"chapter extract fail/short ({len(chapter)})", "label": label})
                print(f"  FAIL extract {label} len={len(chapter)}")
                continue
            pages_ok += 1
            text = clean_thorndike_chapter(prepare_text(chapter, is_html=False))
            if len(text) > MAX_PAGE_CHARS:
                text = text[:MAX_PAGE_CHARS]
            keywords = list(job.get("keywords") or ISLAMIC_KW)
            dens_min = float(job.get("dens_min") or 0.10)
            job_budget = int(job.get("soft_cap") or FAMILY_SOFT_CAP)
            kind = job.get("correspondence_kind")
            typ = job.get("type") or "text"
            reception = job.get("reception_layer")
            license_ = job["license"]
            max_chunks = int(job.get("max_chunks") or job_budget)
            candidates = chunk_paragraphs(text)
            print(f"  chapter_chars={len(text)} candidates={len(candidates)} dens={keyword_density(text, keywords):.3f} job_budget={job_budget}")
            wrote = 0
            for chunk in candidates:
                if atoms_written >= TARGET_MAX or by_family[family] >= FAMILY_SOFT_CAP:
                    break
                if wrote >= min(job_budget, max_chunks):
                    break
                chunk = strip_chrome(chunk).strip()
                if not accept_chunk(chunk, False, keywords, dens_min=dens_min):
                    atoms_skipped_quality += 1
                    continue
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
                    "type": typ if typ in ("text", "table", "correspondence", "diagram_desc") else "text",
                    "text": chunk,
                    "license": license_,
                    "source_url": job["source_url"],
                    "epistemic": "INFERRED",
                    "content_hash": chash,
                    "lens_hints": lens_for(family, typ, kind),
                    "harvest_run": RUN_ID,
                    "reception_layer": reception,
                }
                with ATOMS_PATH.open("a") as f:
                    f.write(json.dumps(atom, ensure_ascii=False) + "\n")
                existing.add(chash)
                atoms_written += 1
                by_family[family] += 1
                by_kind[kind or "?"] += 1
                type_counts[atom["type"]] += 1
                wrote += 1
                if len(sample_ids) < 14:
                    sample_ids.append(aid)
            print(f"  wrote={wrote}")

        # ---- Sacred-texts HTML jobs ----
        for job in HTML_PLAN:
            if atoms_written >= TARGET_MAX:
                break
            family = job["family_id"]
            license_ = job["license"]
            if license_ not in {"public-domain", "pd-us", "cc0", "cc-by"}:
                holds.append({"family_id": family, "reason": f"unclear license {license_}"})
                continue
            reception = job.get("reception_layer")
            typ = job.get("type") or "text"
            kind = job.get("correspondence_kind")
            job_budget = int(job.get("soft_cap") or FAMILY_SOFT_CAP)
            keywords = list(job.get("keywords") or ISLAMIC_KW)
            dens_min = float(job.get("dens_min") or 0.10)
            require_any = job.get("require_any")
            print(f"\n=== HTML {family}/{kind} job_budget={job_budget} ===")
            wrote_job = 0

            for url in [normalize_url(u) for u in (job.get("urls") or [])]:
                if atoms_written >= TARGET_MAX or by_family[family] >= FAMILY_SOFT_CAP or wrote_job >= job_budget:
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

                print(f"  fetch {url}")
                result = fetch_urllib(url)
                mode = "urllib"
                if result["ok"]:
                    preview = prepare_text(result["body"], result.get("is_html", True))
                    if is_chrome_only(preview) and crawler is not None:
                        result = await fetch_crawl4ai(crawler, url)
                        mode = "crawl4ai"
                elif crawler is not None and result.get("status") != 404:
                    result = await fetch_crawl4ai(crawler, url)
                    mode = "crawl4ai"

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
                    if status != 404 and "404" not in str(err):
                        host_fail_streak[host] += 1
                        if host_fail_streak[host] >= HOST_FAIL_SKIP:
                            skipped_hosts.add(host)
                    continue

                host_fail_streak[host] = 0
                pages_ok += 1
                body = result.get("body") or ""
                text = prepare_text(body, result.get("is_html", True))
                if len(text) > MAX_PAGE_CHARS:
                    text = text[:MAX_PAGE_CHARS]
                if is_chrome_only(text) and len(text) < MIN_PROSE:
                    holds.append({"url": url, "reason": "DROP SPA/chrome-only after strip_chrome"})
                    print(f"    DROP chrome-only ({len(text)} chars)")
                    continue

                dens = keyword_density(text, keywords)
                if dens < dens_min * 0.5:
                    print(f"    skip page low dens={dens:.3f}")
                    atoms_skipped_quality += 1
                    continue

                wrote_page = 0
                for chunk in chunk_paragraphs(text):
                    if by_family[family] >= FAMILY_SOFT_CAP or atoms_written >= TARGET_MAX or wrote_job >= job_budget:
                        break
                    chunk = strip_chrome(chunk).strip()
                    if not accept_chunk(chunk, typ == "table", keywords, dens_min=dens_min, require_any=require_any):
                        atoms_skipped_quality += 1
                        continue
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
                        "type": typ if typ in ("text", "table", "correspondence", "diagram_desc") else "text",
                        "text": chunk,
                        "license": license_,
                        "source_url": canon_source_url(url),
                        "epistemic": "INFERRED",
                        "content_hash": chash,
                        "lens_hints": lens_for(family, typ, kind),
                        "harvest_run": RUN_ID,
                        "reception_layer": reception,
                    }
                    with ATOMS_PATH.open("a") as f:
                        f.write(json.dumps(atom, ensure_ascii=False) + "\n")
                    existing.add(chash)
                    atoms_written += 1
                    by_family[family] += 1
                    by_kind[kind or "?"] += 1
                    type_counts[atom["type"]] += 1
                    wrote_page += 1
                    wrote_job += 1
                    if len(sample_ids) < 14:
                        sample_ids.append(aid)
                print(f"    prose={len(text)} wrote={wrote_page} dens={dens:.3f} job_total={wrote_job}")

    finally:
        if crawler_cm is not None:
            await crawler_cm.__aexit__(None, None, None)

    after = family_counts()
    after_total = sum(after.values())
    by_family_new = dict(by_family)

    if atoms_written < TARGET_MIN:
        holds.append({
            "reason": f"below TARGET_MIN {TARGET_MIN} (got {atoms_written}) — quality gate preferred over flood",
        })
    if atoms_written > TARGET_MAX:
        holds.append({"reason": f"note: exceeded TARGET_MAX soft preference ({atoms_written})"})

    receipt = {
        "run_id": RUN_ID,
        "job_type": "harvest",
        "priority": "C",
        "engine": "crawl4ai",
        "engine_version": "0.9.3",
        "fetch_notes": (
            "Gutenberg Thorndike 1923 vols local plaintext chapter slices; "
            "urllib archive.sacred-texts.com PD HTML; crawl4ai fallback"
        ),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "allowlist": sorted(ALLOW_HOSTS),
        "user_agent": UA,
        "rate_limit_sec": SLEEP_SEC,
        "epistemic": "INFERRED",
        "focus_family": "islamic_occult_pd",
        "atom_types": ["text", "table", "correspondence", "diagram_desc"],
        "type_counts": dict(type_counts),
        "by_correspondence_kind": dict(by_kind),
        "pages_ok": pages_ok,
        "pages_fail": pages_fail,
        "atoms_written": atoms_written,
        "atoms_skipped_dupe": atoms_skipped_dupe,
        "atoms_skipped_quality": atoms_skipped_quality,
        "by_family_new": by_family_new,
        "before_by_family": dict(before),
        "after_by_family": dict(after),
        "before_total": before_total,
        "after_total": after_total,
        "family_delta": {
            "islamic_occult_pd": after.get("islamic_occult_pd", 0) - before.get("islamic_occult_pd", 0),
        },
        "urls": urls_attempted,
        "FAILED": failures,
        "HOLD": holds,
        "license_notes": license_notes,
        "gutenberg_cache": cache_notes,
        "chrome_strip": True,
        "no_firecrawl": True,
        "no_wave3b_harvest": True,
        "no_enochian_flood": True,
        "no_git_commit_atoms": True,
        "no_efficacy": True,
        "atoms_path": str(ATOMS_PATH),
        "backup": str(backup),
        "sample_atom_ids": sample_ids,
        "skipped_hosts": sorted(skipped_hosts),
        "target_range": [TARGET_MIN, TARGET_MAX],
        "proposals": {
            "KEEP": ["islamic_occult_pd"] if by_family_new.get("islamic_occult_pd") else [],
            "HOLD": [h for h in holds if "DROP" not in str(h.get("reason", ""))],
            "DROP": [h for h in holds if "DROP" in str(h.get("reason", ""))],
        },
    }
    receipt_path = RECEIPTS_DIR / f"{RUN_ID}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False))

    fid = "islamic_occult_pd"
    b = before.get(fid, 0)
    a = after.get(fid, 0)
    lines = [
        f"# Ingest Priority C scoreboard — islamic_occult_pd (Picatrix / Arabic occult-scientific PD)",
        f"",
        f"- run_id: `{RUN_ID}`",
        f"- job_type: harvest | priority: **C** | engine: crawl4ai 0.9.3 (+ urllib + local Gutenberg)",
        f"- timestamp_utc: {receipt['timestamp_utc']}",
        f"- pages_ok: **{pages_ok}** | pages_fail: **{pages_fail}**",
        f"- atoms_written: **{atoms_written}** | dupes: {atoms_skipped_dupe} | quality_skips: {atoms_skipped_quality}",
        f"- before_total: **{before_total}** → after_total: **{after_total}**",
        f"- family `{fid}`: **{b} → {a}** (delta {a - b:+d})",
        f"- types: `{dict(type_counts)}`",
        f"- kinds: `{dict(by_kind)}`",
        f"- receipt: `{receipt_path}`",
        f"- backup: `{backup}`",
        f"- script: `/workspace/Athanor/scripts/shadow/athanor/ingest_priority_c.py`",
        f"- chrome_strip: yes | allowlist respected | no Firecrawl | no Wave 3b | no Enochian | no efficacy | no Hub",
        f"",
        f"## Priority C family delta",
        f"",
        f"| family_id | before | after | delta | % of NEW |",
        f"|---|---:|---:|---:|---:|",
        f"| `{fid}` | {b} | {a} | {a - b:+d} | {100.0 if atoms_written else 0:.1f}% |",
        f"",
        f"## Sources used",
        f"",
        f"- Gutenberg Thorndike 1923 vol1 ch28 Arabic occult science; ch30 Gerbert/Arabic astrology",
        f"- Gutenberg Thorndike 1923 vol2 ch38 Arabic astrology translators; ch66 Picatrix",
        f"- sacred-texts: de Boer HPI (Brethren/Kindi/natural phil.); O'Leary Arabic Thought (translators/Arab period)",
        f"- sacred-texts: Pavitt Book of Talismans (Arab/Islamic-historical leaves only)",
        f"",
        f"## HOLD (with reason)",
        f"",
    ]
    for h in holds:
        lines.append(f"- {json.dumps(h, ensure_ascii=False)}")
    lines += [
        f"",
        f"## FAILED",
        f"",
    ]
    if not failures:
        lines.append("- (none)")
    else:
        for fail in failures[:80]:
            lines.append(f"- {fail.get('url')}: {fail.get('error')} (status={fail.get('status')})")
    lines += [
        f"",
        f"## INFERRED license notes",
        f"",
    ]
    for n in license_notes:
        lines.append(f"- {n}")
    lines += [
        f"",
        f"## Sample atom_ids",
        f"",
    ]
    for s in sample_ids:
        lines.append(f"- `{s}`")
    lines += [
        f"",
        f"## Propose (never GOLD)",
        f"",
        f"- KEEP: islamic_occult_pd ({atoms_written} NEW via Thorndike Picatrix/Arabic occult PD + sacred-texts Islamic scientific)",
        f"- HOLD: modern English Picatrix (Warnock/Greer/Atallah/Hashem); Alfonso concordance CC-BY-ND; Arabic Ghayat license-unclear; Wave 3b; Enochian",
        f"- DROP: SPA chrome-only after strip; HTTP failures (no invented excerpt)",
        f"",
    ]
    scoreboard_path = SCOREBOARD_DIR / f"ingest-priority-c-{TS_FILE}.md"
    scoreboard_path.write_text("\n".join(lines) + "\n")

    try:
        shutil.copy2(Path(__file__), SCOREBOARD_DIR / "ingest_priority_c.py")
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
        "islamic_occult_pd_before": b,
        "islamic_occult_pd_after": a,
        "by_family_new": by_family_new,
        "receipt": str(receipt_path),
        "scoreboard": str(scoreboard_path),
        "backup": str(backup),
    }
    print("\n=== SUMMARY ===")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
