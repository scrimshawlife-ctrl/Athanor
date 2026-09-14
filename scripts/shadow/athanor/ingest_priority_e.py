#!/usr/bin/env python3
"""ATHANOR-INGEST Priority E — Wave 3 PD reception only.

Families: golden_dawn_hist, theosophy_pd, folk_magic_pd, chaos_spare_hist
(reception_layer=modern_reception; historical_commentary for pre-modern folk prose).

Wave 3b PROPOSAL ONLY — do not harvest: thelema_pd, wicca_hist, spiritualism_pd,
new_thought_pd, ceremonial_revival_hist, neopagan_recon_hist, atr_open_hist, chaos_late_hist.

Local SoT only. No Firecrawl, no Enochian flood, no HF upload, no git-commit of atoms.
Balance: no family > 25% of NEW this run. PD-only. epistemic=INFERRED.
Access language only — no efficacy/summon.
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
CACHE_DIR = SCOREBOARD_DIR / "cache-e"
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
    "collectionapi.metmuseum.org",
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
FAMILY_SOFT_CAP = 65  # prefer ~40–80; hard balance ≤25% NEW
TARGET_MIN = 140
TARGET_MAX = 260
HOST_FAIL_SKIP = 2
MAX_FAMILY_SHARE = 0.25

FOCUS_FAMILIES = [
    "golden_dawn_hist",
    "theosophy_pd",
    "folk_magic_pd",
    "chaos_spare_hist",
]

WAVE3B_HOLD = [
    "thelema_pd",
    "wicca_hist",
    "spiritualism_pd",
    "new_thought_pd",
    "ceremonial_revival_hist",
    "neopagan_recon_hist",
    "atr_open_hist",
    "chaos_late_hist",
]

RUN_TS = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
RUN_ID = f"ingest-priority-e-{RUN_TS}-{uuid.uuid4().hex[:8]}"
TS_FILE = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
BACKUP_NAME = f"atoms.pre-ingest-e-{RUN_TS}.jsonl"

MIRROR_HOST = "https://archive.sacred-texts.com"
CANON_HOST = "https://sacred-texts.com"

# ---------------------------------------------------------------------------
# Keywords
# ---------------------------------------------------------------------------
GD_KW = [
    "golden", "dawn", "hermetic", "westcott", "mathers", "waite", "order",
    "kabbalah", "qabalah", "sephiroth", "hermes", "rosicrucian", "occult",
    "adept", "temple", "cipher", "theosophy", "fratres", "sorores", "ritual",
    "ceremony", "magic", "magical", "elemental", "grade", "neophyte",
    "introduction", "historical", "manuscript", "translation",
]
THEOS_KW = [
    "theosophy", "blavatsky", "secret doctrine", "isis", "adept", "occult",
    "mahatma", "atma", "buddhi", "manas", "astral", "plane", "reincarnation",
    "karma", "root race", "stanzas", "dzyan", "logos", "cosmic", "evolution",
    "esoteric", "leadbeater", "steiner", "clairvoyance", "aura", "monad",
    "hierarchy", "wisdom", "doctrine", "philosophy", "symbol",
]
FOLK_KW = [
    "magic", "magical", "folk", "witch", "witchcraft", "charm", "taboo",
    "spirit", "tree", "king", "priest", "ritual", "custom", "tradition",
    "sympathetic", "contagious", "frazer", "grimm", "fairy", "tale",
    "spell", "superstition", "peasant", "europe", "folklore", "soul",
    "mother", "holle", "enchant", "forest", "village", "belief",
]
SPARE_KW = [
    "spare", "zos", "kia", "sigil", "anathema", "pleasure", "focus",
    "automatic", "will", "self", "neither", "neither-neither", "belief",
    "atavism", "sorcery", "artist", "ecstasy", "conscious", "unconscious",
    "symbol", "desire", "magick", "magic", "hypocrite", "sermon",
]

HOLD_STATIC = [
    {
        "url": "https://sacred-texts.com/eso/ (Regardie / modern GD manuals)",
        "reason": "HOLD — Israel Regardie Golden Dawn materials remain copyright; not harvested",
    },
    {
        "url": "https://sacred-texts.com/eso/chaos/zos.txt",
        "reason": "HOLD — Kenneth Grant Cults of the Shadow excerpt (copyright)",
    },
    {
        "url": "https://sacred-texts.com/eso/chaos/sparezia.txt",
        "reason": "HOLD — modern secondary commentary (1993 Usenet), not clear PD Spare primary",
    },
    {
        "url": "https://sacred-texts.com/eso/chaos/chaosdef.htm",
        "reason": "HOLD — modern Defining Chaos; chaos_late_hist / Wave 3b-adjacent",
    },
    {
        "url": "https://sacred-texts.com/eso/chaos/monastic.txt",
        "reason": "HOLD — modern Chaos Monasticism; not historical Spare PD",
    },
    {
        "note": "TOPY materials — HOLD (modern; chaos_late_hist / Wave 3b-adjacent)",
        "paths": [
            "/eso/topy/topybook.txt",
            "/eso/topy/topymani.htm",
            "/eso/topy/black.htm",
            "/eso/topy/topyfaq.txt",
        ],
    },
    {
        "note": "PA Dutch Pow-Wows / Long Lost Friend operational charm leaves — HOLD efficacy framing",
        "paths": ["/ame/pow/pow003.htm", "/ame/pow/pow012.htm", "/ame/pow/pow016.htm"],
    },
    {
        "note": "Waite Book of Ceremonial Magic conjuration/demon catalog leaves — HOLD summon/efficacy",
        "paths": ["/grim/bcm/bcm51.htm", "/grim/bcm/bcm61.htm", "/grim/bcm/bcm63.htm"],
    },
    {"family_id": "enochian", "reason": "HOLD — Priority F = no new Enochian; out of Priority E scope"},
    {
        "note": "Wave 3b families — PROPOSAL ONLY; do not harvest",
        "family_ids": WAVE3B_HOLD,
    },
    {
        "note": "Spare UK copyright life+70 (d.1956) may still apply in UK until end-2026; harvested only as PD-US published ≤1927 with INFERRED license note",
    },
]


def mh(*paths: str) -> list[str]:
    return [f"{MIRROR_HOST}{p}" for p in paths]


# ---------------------------------------------------------------------------
# HTML harvest plan (balanced soft_caps)
# ---------------------------------------------------------------------------
HTML_PLAN: list[dict[str, Any]] = [
    # ---- golden_dawn_hist ----
    {
        "family_id": "golden_dawn_hist",
        "license": "public-domain",
        "reception_layer": "modern_reception",
        "type": "text",
        "correspondence_kind": "westcott-historic-lecture",
        "urls": mh("/eso/historic.htm"),
        "soft_cap": 8,
        "keywords": GD_KW,
        "dens_min": 0.06,
        "license_note": "W. Wynn Westcott Historic Lecture on the Order of the G.D. — PD historical (INFERRED)",
    },
    {
        "family_id": "golden_dawn_hist",
        "license": "public-domain",
        "reception_layer": "modern_reception",
        "type": "text",
        "correspondence_kind": "mathers-kabbalah-unveiled-hist",
        "urls": mh(
            "/jud/tku/tku00.htm",
            "/jud/tku/tku01.htm",
            "/jud/tku/tku02.htm",
            "/jud/tku/tku03.htm",
            "/jud/tku/tku04.htm",
            "/jud/tku/tku05.htm",
            "/jud/tku/tku06.htm",
            "/jud/tku/tku07.htm",
            "/jud/tku/tku08.htm",
            "/jud/tku/tku09.htm",
            "/jud/tku/tku10.htm",
            "/jud/tku/tku11.htm",
            "/jud/tku/tku12.htm",
            "/jud/tku/tku13.htm",
            "/jud/tku/tku14.htm",
            "/jud/tku/tku15.htm",
            "/jud/tku/tku16.htm",
            "/jud/tku/tku17.htm",
            "/jud/tku/tku18.htm",
            "/jud/tku/tku20.htm",
            "/jud/tku/tku22.htm",
            "/jud/tku/tku24.htm",
            "/jud/tku/tku26.htm",
            "/jud/tku/tku28.htm",
            "/jud/tku/tku30.htm",
        ),
        "soft_cap": 40,
        "keywords": GD_KW,
        "dens_min": 0.05,
        "license_note": "S.L. MacGregor Mathers, Kabbalah Unveiled (1887) — PD GD historical reception (INFERRED)",
    },
    {
        "family_id": "golden_dawn_hist",
        "license": "public-domain",
        "reception_layer": "modern_reception",
        "type": "text",
        "correspondence_kind": "waite-bcm-historical-survey",
        "urls": mh(
            "/grim/bcm/bcm03.htm",
            "/grim/bcm/bcm04.htm",
            "/grim/bcm/bcm05.htm",
            "/grim/bcm/bcm06.htm",
            "/grim/bcm/bcm07.htm",
            "/grim/bcm/bcm08.htm",
            "/grim/bcm/bcm09.htm",
            "/grim/bcm/bcm12.htm",
            "/grim/bcm/bcm13.htm",
            "/grim/bcm/bcm19.htm",
            "/grim/bcm/bcm80.htm",
        ),
        "soft_cap": 28,
        "keywords": GD_KW,
        "dens_min": 0.05,
        "description_only": True,
        "license_note": "A.E. Waite Book of Ceremonial Magic (1911) historical survey leaves only; conjuration leaves HOLD (INFERRED)",
    },
    # ---- theosophy_pd ----
    {
        "family_id": "theosophy_pd",
        "license": "public-domain",
        "reception_layer": "modern_reception",
        "type": "text",
        "correspondence_kind": "blavatsky-isis-unveiled",
        "urls": mh(
            "/the/iu/iu000.htm",
            "/the/iu/iu001.htm",
            "/the/iu/iu002.htm",
            "/the/iu/iu003.htm",
            "/the/iu/iu004.htm",
            "/the/iu/iu005.htm",
            "/the/iu/iu006.htm",
            "/the/iu/iu007.htm",
            "/the/iu/iu008.htm",
            "/the/iu/iu010.htm",
            "/the/iu/iu012.htm",
            "/the/iu/iu100.htm",
            "/the/iu/iu101.htm",
            "/the/iu/iu102.htm",
            "/the/iu/iu103.htm",
            "/the/iu/iu105.htm",
            "/the/iu/iu108.htm",
            "/the/iu/iu110.htm",
        ),
        "soft_cap": 28,
        "keywords": THEOS_KW,
        "dens_min": 0.05,
        "license_note": "H.P. Blavatsky Isis Unveiled (1877) — public-domain (INFERRED)",
    },
    {
        "family_id": "theosophy_pd",
        "license": "public-domain",
        "reception_layer": "modern_reception",
        "type": "text",
        "correspondence_kind": "blavatsky-secret-doctrine",
        "urls": mh(
            "/the/sd/sd1-0-in.htm",
            "/the/sd/sd1-0-pr.htm",
            "/the/sd/sd1-1-01.htm",
            "/the/sd/sd1-1-02.htm",
            "/the/sd/sd1-1-03.htm",
            "/the/sd/sd1-1-04.htm",
            "/the/sd/sd1-1-05.htm",
            "/the/sd/sd1-1-06.htm",
            "/the/sd/sd1-1-07.htm",
            "/the/sd/sd1-1-08.htm",
            "/the/sd/sd1-2-01.htm",
            "/the/sd/sd1-2-02.htm",
            "/the/sd/sd1-2-03.htm",
            "/the/sd/sd1-2-04.htm",
            "/the/sd/sd2-1-01.htm",
            "/the/sd/sd2-1-02.htm",
            "/the/sd/sd2-1-03.htm",
            "/the/sd/sd2-2-01.htm",
        ),
        "soft_cap": 28,
        "keywords": THEOS_KW,
        "dens_min": 0.05,
        "license_note": "H.P. Blavatsky The Secret Doctrine (1888) — public-domain (INFERRED)",
    },
    {
        "family_id": "theosophy_pd",
        "license": "public-domain",
        "reception_layer": "modern_reception",
        "type": "text",
        "correspondence_kind": "leadbeater-textbook-theosophy",
        "urls": mh(
            "/the/tot/chap01.htm",
            "/the/tot/chap02.htm",
            "/the/tot/chap03.htm",
            "/the/tot/chap04.htm",
            "/the/tot/chap05.htm",
            "/the/tot/chap06.htm",
            "/the/tot/chap07.htm",
            "/the/tot/chap08.htm",
            "/the/tot/chap09.htm",
            "/the/tot/chap10.htm",
        ),
        "soft_cap": 18,
        "keywords": THEOS_KW,
        "dens_min": 0.06,
        "license_note": "C.W. Leadbeater A Textbook of Theosophy (1912) — public-domain (INFERRED)",
    },
    {
        "family_id": "theosophy_pd",
        "license": "public-domain",
        "reception_layer": "modern_reception",
        "type": "text",
        "correspondence_kind": "steiner-theosophy-1910",
        "urls": mh(
            "/eso/theo/theo01.htm",
            "/eso/theo/theo02.htm",
            "/eso/theo/theo03.htm",
            "/eso/theo/theo04.htm",
            "/eso/theo/theo05.htm",
            "/eso/theo/theo06.htm",
            "/eso/theo/theo07.htm",
        ),
        "soft_cap": 14,
        "keywords": THEOS_KW,
        "dens_min": 0.05,
        "license_note": "Rudolf Steiner Theosophy tr. Shields (1910) — public-domain (INFERRED)",
    },
    # ---- folk_magic_pd ----
    {
        "family_id": "folk_magic_pd",
        "license": "public-domain",
        "reception_layer": "modern_reception",
        "type": "text",
        "correspondence_kind": "frazer-golden-bough-folk",
        "urls": mh(
            "/pag/frazer/gb00301.htm",
            "/pag/frazer/gb00302.htm",
            "/pag/frazer/gb00303.htm",
            "/pag/frazer/gb00304.htm",
            "/pag/frazer/gb00400.htm",
            "/pag/frazer/gb00501.htm",
            "/pag/frazer/gb00600.htm",
            "/pag/frazer/gb00901.htm",
            "/pag/frazer/gb00902.htm",
            "/pag/frazer/gb01000.htm",
            "/pag/frazer/gb01500.htm",
            "/pag/frazer/gb01801.htm",
            "/pag/frazer/gb01802.htm",
            "/pag/frazer/gb01803.htm",
            "/pag/frazer/gb01901.htm",
            "/pag/frazer/gb01902.htm",
            "/pag/frazer/gb01903.htm",
            "/pag/frazer/gb01904.htm",
            "/pag/frazer/gb01905.htm",
            "/pag/frazer/gb00101.htm",
            "/pag/frazer/gb00200.htm",
        ),
        "soft_cap": 45,
        "keywords": FOLK_KW,
        "dens_min": 0.05,
        "description_only": True,
        "license_note": "J.G. Frazer Golden Bough (abridged PD leaves on sacred-texts) — anthropological folk-magic reception (INFERRED)",
    },
    {
        "family_id": "folk_magic_pd",
        "license": "public-domain",
        "reception_layer": "historical_commentary",
        "type": "text",
        "correspondence_kind": "grimm-folk-tradition-prose",
        "urls": mh(
            "/neu/grimm/ht01.htm",
            "/neu/grimm/ht02.htm",
            "/neu/grimm/ht06.htm",
            "/neu/grimm/ht11.htm",
            "/neu/grimm/ht12.htm",
            "/neu/grimm/ht15.htm",
            "/neu/grimm/ht19.htm",
            "/neu/grimm/ht20.htm",
            "/neu/grimm/ht21.htm",
            "/neu/grimm/ht23.htm",
            "/neu/grimm/ht24.htm",
            "/neu/grimm/ht07.htm",
            "/neu/grimm/ht09.htm",
            "/neu/grimm/ht13.htm",
        ),
        "soft_cap": 28,
        "keywords": FOLK_KW,
        "dens_min": 0.04,
        "license_note": "Grimm Household Tales (PD English) — tradition-prose folk motifs only, not Wikipedia (INFERRED)",
    },
    # ---- chaos_spare_hist (grow carefully) ----
    {
        "family_id": "chaos_spare_hist",
        "license": "pd-us",
        "reception_layer": "modern_reception",
        "type": "text",
        "correspondence_kind": "spare-focus-of-life",
        "urls": mh("/eso/chaos/focus.htm"),
        "soft_cap": 12,
        "keywords": SPARE_KW,
        "dens_min": 0.04,
        "license_note": "Austin Osman Spare The Focus of Life (1921) — PD-US; UK term may differ until end-2026 (INFERRED)",
    },
    {
        "family_id": "chaos_spare_hist",
        "license": "pd-us",
        "reception_layer": "modern_reception",
        "type": "text",
        "correspondence_kind": "spare-anathema-of-zos",
        "urls": mh("/eso/chaos/anathema.txt"),
        "soft_cap": 10,
        "keywords": SPARE_KW,
        "dens_min": 0.04,
        "license_note": "Austin Osman Spare Anathema of Zos (1927) — PD-US; UK term may differ until end-2026 (INFERRED)",
    },
]

GUTENBERG_JOBS: list[dict[str, Any]] = [
    {
        "family_id": "theosophy_pd",
        "license": "public-domain",
        "reception_layer": "modern_reception",
        "type": "text",
        "correspondence_kind": "blavatsky-key-to-theosophy",
        "source_url": "https://www.gutenberg.org/ebooks/55618",
        "txt_url": "https://www.gutenberg.org/files/55618/55618-0.txt",
        "local_path": str(CACHE_DIR / "pg55618.txt"),
        "soft_cap": 18,
        "keywords": THEOS_KW,
        "dens_min": 0.05,
        "license_note": "H.P. Blavatsky The Key to Theosophy — Project Gutenberg #55618 public-domain (INFERRED)",
    },
]

LICENSE_NOTES = [
    "Westcott Historic Lecture (G.D.): public-domain sacred-texts (INFERRED).",
    "Mathers Kabbalah Unveiled (1887): public-domain GD historical reception (INFERRED).",
    "Waite Book of Ceremonial Magic (1911): PD historical survey leaves only; conjuration/demon leaves HOLD (INFERRED).",
    "Regardie Golden Dawn corpus: HOLD copyright.",
    "Blavatsky Isis Unveiled (1877) + Secret Doctrine (1888): public-domain (INFERRED).",
    "Blavatsky Key to Theosophy: Gutenberg #55618 public-domain (INFERRED).",
    "Leadbeater Textbook of Theosophy (1912): public-domain (INFERRED).",
    "Steiner Theosophy tr. Shields (1910): public-domain (INFERRED).",
    "Frazer Golden Bough PD leaves: anthropological folk-magic reception (INFERRED).",
    "Grimm Household Tales PD English: tradition-prose folk motifs (INFERRED).",
    "PA Dutch Pow-Wows / Hohman Long Lost Friend: HOLD efficacy/charm operational leaves.",
    "Spare Focus of Life (1921) + Anathema of Zos (1927): PD-US (INFERRED); UK life+70 may apply until end-2026.",
    "Kenneth Grant Cults of the Shadow Spare excerpt (zos.txt): HOLD copyright.",
    "Modern chaos commentary / TOPY / Defining Chaos / Monasticism: HOLD (chaos_late / Wave 3b).",
    "Wave 3b families: PROPOSAL ONLY — not harvested.",
    "Enochian: HOLD — Priority F = no new Enochian.",
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
        r"(?i)^buy (it here|the internet|disk|this book|this Book)",
        r"(?i)^wisdom is priceless",
        r"(?i)^see site copyrights",
        r"(?i)^powered by",
        r"(?i)^search$",
        r"(?i)^faq$",
        r"(?i)^contact$",
        r"(?i)^theosophy$",
        r"(?i)^esoteric$",
        r"(?i)^occult$",
        r"(?i)^neopaganism$",
        r"(?i)^project gutenberg",
        r"(?i)^the project gutenberg eBook",
        r"(?i)^this eBook is for the use of anyone",
        r"(?i)^\*\*\* START OF",
        r"(?i)^\*\*\* END OF",
        r"(?i)^Subject:",
        r"(?i)^Lines:",
        r"(?i)^Date:",
        r"(?i)^From:",
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


def strip_gutenberg_boilerplate(text: str) -> str:
    start = re.search(r"\*\*\*\s*START OF[^\n]*\*\*\*", text, re.I)
    if start:
        text = text[start.end() :]
    end = re.search(r"\*\*\*\s*END OF[^\n]*\*\*\*", text, re.I)
    if end:
        text = text[: end.start()]
    return text.strip()


def strip_sacred_texts_title_chrome(text: str) -> str:
    """Remove '| Internet Sacred Text Archive' title crumbs and leading nav titles."""
    if not text:
        return ""
    # Drop first line(s) that are page-title chrome
    lines = text.splitlines()
    out = []
    for i, line in enumerate(lines):
        s = line.strip()
        if not s:
            if out:
                out.append("")
            continue
        if "internet sacred text archive" in s.lower():
            # Keep anything after the archive marker if substantial
            parts = re.split(r"(?i)\|\s*Internet Sacred Text Archive", s, maxsplit=1)
            if len(parts) == 2 and len(parts[1].strip()) >= 80:
                out.append(parts[1].strip())
            continue
        if i < 3 and re.match(r"(?i)^(judaism|grimoires|theosophy|esoteric|occult|neopaganism|northern european|americana)\s*$", s):
            continue
        if i < 4 and re.match(r"(?i)^p\.\s*\w+\s*$", s):
            continue
        if i < 2 and re.match(r"(?i)^click to (enlarge|view)\b", s):
            continue
        out.append(line)
    text = "\n".join(out)
    text = re.sub(r"(?is)This HTML version\s*©.*?All rights reserved\.\s*", " ", text)
    text = re.sub(r"(?i)\|\s*Internet Sacred Text Archive", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def prepare_text(raw_md_or_html: str, is_html: bool) -> str:
    if is_html:
        text = html_to_text(raw_md_or_html)
    else:
        text = raw_md_or_html or ""
    text = clean_nav_lines(text)
    text = strip_sacred_texts_title_chrome(text)
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
    """Skip operational/efficacy framing; keep historical access language."""
    low = text.lower()
    bad = [
        r"(?i)\bsummon(?:s|ed|ing)?\s+(?:the\s+)?(?:spirit|demon|angel|jinn)",
        r"(?i)\bthis will cause\b",
        r"(?i)\bto make a woman love\b",
        r"(?i)\bsay this conjuration\b",
        r"(?i)\bguaranteed results\b",
        r"(?i)\battaining health, wealth",
        r"(?i)\byou will obtain\b",
        r"(?i)\bthis practice will\b",
        r"(?i)\bhow to obtain things which are desired\b",
        r"(?i)\bto attach a dog to a person\b",
        r"(?i)\bhand of glory\b.*\bperform\b",
        r"(?i)\btrue method of making pacts\b",
    ]
    hits = sum(1 for p in bad if re.search(p, text))
    if hits >= 1 and not any(
        w in low
        for w in (
            "history",
            "historical",
            "manuscript",
            "century",
            "translation",
            "chapter",
            "doctrine",
            "described",
            "according to",
            "frazer",
            "waite remarks",
            "the author observes",
        )
    ):
        return True
    return False


def is_practice_results_frame(text: str) -> bool:
    """Block practice-as-results / conjuration instruction leaves."""
    low = text.lower()
    patterns = [
        r"(?i)\bdo the following visualization\b",
        r"(?i)\brepeat this mantra\s+\d+\s+times\b",
        r"(?i)\bsay unto him\b.*\bI conjure\b",
        r"(?i)\bI conjure thee\b",
        r"(?i)\bthe operator shall\b.*\bcircle\b",
        r"(?i)\bguaranteed enlightenment\b",
        r"(?i)\bto cause love\b",
        r"(?i)\binvisibility experiment\b",
    ]
    if any(re.search(p, text) for p in patterns):
        if any(
            w in low
            for w in (
                "describes",
                "according to",
                "historically",
                "waite observes",
                "the text states",
                "survey of",
                "literature of",
            )
        ):
            return False
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
    if typ in ("table", "correspondence", "diagram_desc"):
        base["symbolic"] = True
    if kind:
        base["correspondence_kind"] = kind
    if family_id in ("folk_magic_pd", "golden_dawn_hist", "chaos_spare_hist", "theosophy_pd"):
        base["operational"] = False
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
            if "application/json" in ctype or url.endswith(".txt"):
                is_html = False
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


def accept_chunk(
    chunk: str,
    is_table: bool,
    keywords: list[str],
    dens_min: float = 0.10,
    require_any: list[str] | None = None,
    description_only: bool = False,
) -> bool:
    chunk = chunk.strip()
    if not chunk:
        return False
    if "internet sacred text archive" in chunk.lower()[:180]:
        return False
    if is_efficacy_frame(chunk):
        return False
    if description_only and is_practice_results_frame(chunk):
        return False
    if not has_require_any(chunk, require_any):
        return False
    if is_table or looks_like_table_text(chunk):
        return len(chunk) >= MIN_TABLE_ATOM or (len(chunk) >= 80 and looks_like_table_text(chunk))
    dens = keyword_density(chunk, keywords) if keywords else 1.0
    if len(chunk) < MIN_ATOM:
        if len(chunk) >= 280 and dens >= max(dens_min, 0.12):
            return True
        return False
    return dens >= dens_min


def backup_corpus() -> Path:
    dest = ATOMS_PATH.parent / BACKUP_NAME
    if ATOMS_PATH.exists():
        if not dest.exists():
            shutil.copy2(ATOMS_PATH, dest)
    return dest


def family_share_ok(by_family: dict[str, int], family: str, atoms_written: int) -> bool:
    """Cap each family at min(FAMILY_SOFT_CAP, floor(MAX_FAMILY_SHARE * TARGET_MAX))."""
    # chaos_spare grows carefully: hard soft-cap 20 NEW this run
    if family == "chaos_spare_hist":
        return by_family.get(family, 0) < 20
    per_family_max = min(FAMILY_SOFT_CAP, int(TARGET_MAX * MAX_FAMILY_SHARE))
    return by_family.get(family, 0) < per_family_max


def ensure_gutenberg_cache() -> list[dict]:
    notes = []
    for job in GUTENBERG_JOBS:
        lp = Path(job["local_path"])
        url = job["txt_url"]
        if lp.exists() and lp.stat().st_size > 1000:
            notes.append({"path": str(lp), "url": url, "cached": True})
            continue
        print(f"fetch gutenberg {url}")
        result = fetch_urllib(url)
        if not result["ok"]:
            notes.append({"path": str(lp), "url": url, "cached": False, "error": result.get("error")})
            continue
        lp.write_text(result["body"], encoding="utf-8")
        notes.append({"path": str(lp), "url": url, "cached": True, "bytes": lp.stat().st_size})
        import time as _time
        _time.sleep(SLEEP_SEC)
    return notes


def write_atom(
    *,
    family: str,
    typ: str,
    chunk: str,
    license_: str,
    source_url: str,
    reception: str,
    kind: str | None,
    existing: set[str],
    by_family: dict[str, int],
    by_kind: dict[str, int],
    type_counts: Counter,
    sample_ids: list[str],
) -> bool:
    chash = content_hash(chunk)
    if chash in existing:
        return False
    aid = atom_id_for(family, chash)
    atom = {
        "atom_id": aid,
        "family_id": family,
        "type": typ if typ in ("text", "table", "correspondence", "diagram_desc") else "text",
        "text": chunk,
        "license": license_,
        "source_url": source_url,
        "epistemic": "INFERRED",
        "content_hash": chash,
        "lens_hints": lens_for(family, typ, kind),
        "harvest_run": RUN_ID,
        "reception_layer": reception,
    }
    with ATOMS_PATH.open("a") as f:
        f.write(json.dumps(atom, ensure_ascii=False) + "\n")
    existing.add(chash)
    by_family[family] += 1
    by_kind[kind or "?"] += 1
    type_counts[atom["type"]] += 1
    if len(sample_ids) < 20:
        sample_ids.append(aid)
    return True


async def main() -> None:
    backup = backup_corpus()
    before = family_counts()
    before_total = sum(before.values())
    existing = load_existing_hashes()
    print(f"run_id={RUN_ID} existing_hashes={len(existing)} before_total={before_total}")
    for fid in FOCUS_FAMILIES:
        print(f"  before {fid}={before.get(fid, 0)}")
    print("HAS_CRAWL4AI=", HAS_CRAWL4AI)
    print("backup=", backup)

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
    license_notes = list(LICENSE_NOTES)
    type_counts: Counter = Counter()

    cache_notes = ensure_gutenberg_cache()

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
        # ---- Sacred-texts / HTML jobs ----
        for job in HTML_PLAN:
            if atoms_written >= TARGET_MAX:
                holds.append({"reason": f"TARGET_MAX {TARGET_MAX} reached; stop harvest"})
                break
            family = job["family_id"]
            if family in WAVE3B_HOLD:
                holds.append({"family_id": family, "reason": "HOLD Wave 3b — proposal only"})
                continue
            license_ = job["license"]
            if license_ not in {"public-domain", "pd-us", "cc0", "cc-by"}:
                holds.append({"family_id": family, "reason": f"unclear license {license_}"})
                continue
            if not family_share_ok(by_family, family, atoms_written):
                continue
            reception = job.get("reception_layer")
            typ = job.get("type") or "text"
            kind = job.get("correspondence_kind")
            job_budget = int(job.get("soft_cap") or FAMILY_SOFT_CAP)
            keywords = list(job.get("keywords") or [])
            dens_min = float(job.get("dens_min") or 0.10)
            require_any = job.get("require_any")
            description_only = bool(job.get("description_only"))
            print(f"\n=== HTML {family}/{kind} job_budget={job_budget} ===")
            wrote_job = 0

            for url in [normalize_url(u) for u in (job.get("urls") or [])]:
                if atoms_written >= TARGET_MAX or not family_share_ok(by_family, family, atoms_written) or wrote_job >= job_budget:
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

                dens = keyword_density(text, keywords) if keywords else 1.0
                if dens < dens_min * 0.45:
                    print(f"    skip page low dens={dens:.3f}")
                    atoms_skipped_quality += 1
                    continue

                wrote_page = 0
                for chunk in chunk_paragraphs(text, min_c=MIN_TABLE_ATOM if typ == "table" else MIN_ATOM):
                    if not family_share_ok(by_family, family, atoms_written) or atoms_written >= TARGET_MAX or wrote_job >= job_budget:
                        break
                    chunk = strip_chrome(chunk).strip()
                    if not accept_chunk(
                        chunk,
                        typ == "table",
                        keywords,
                        dens_min=dens_min,
                        require_any=require_any,
                        description_only=description_only,
                    ):
                        atoms_skipped_quality += 1
                        continue
                    if len(chunk) > MAX_ATOM + 400:
                        chunk = chunk[: MAX_ATOM + 400]
                    chash = content_hash(chunk)
                    if chash in existing:
                        atoms_skipped_dupe += 1
                        continue
                    if write_atom(
                        family=family,
                        typ=typ,
                        chunk=chunk,
                        license_=license_,
                        source_url=canon_source_url(url),
                        reception=reception,
                        kind=kind,
                        existing=existing,
                        by_family=by_family,
                        by_kind=by_kind,
                        type_counts=type_counts,
                        sample_ids=sample_ids,
                    ):
                        atoms_written += 1
                        wrote_page += 1
                        wrote_job += 1
                    else:
                        atoms_skipped_dupe += 1
                print(f"    prose={len(text)} wrote={wrote_page} dens={dens:.3f} job_total={wrote_job}")

        # ---- Gutenberg plaintext jobs ----
        for job in GUTENBERG_JOBS:
            if atoms_written >= TARGET_MAX:
                break
            family = job["family_id"]
            if family in WAVE3B_HOLD:
                continue
            if not family_share_ok(by_family, family, atoms_written):
                continue
            lp = Path(job["local_path"])
            if not lp.exists():
                failures.append({"url": job["txt_url"], "error": "gutenberg cache missing"})
                pages_fail += 1
                continue
            print(f"\n=== GUTENBERG {family}/{job['correspondence_kind']} ===")
            raw = lp.read_text(encoding="utf-8", errors="replace")
            text = strip_gutenberg_boilerplate(raw)
            text = prepare_text(text, is_html=False)
            if len(text) > MAX_PAGE_CHARS:
                text = text[:MAX_PAGE_CHARS]
            pages_ok += 1
            urls_attempted.append({
                "url": job["txt_url"],
                "source_url_canon": job["source_url"],
                "family_id": family,
                "kind": job["correspondence_kind"],
                "ok": True,
                "status": 200,
                "error": None,
                "mode": "local-gutenberg",
            })
            keywords = list(job.get("keywords") or [])
            dens_min = float(job.get("dens_min") or 0.05)
            job_budget = int(job.get("soft_cap") or 18)
            wrote_job = 0
            for chunk in chunk_paragraphs(text, min_c=MIN_ATOM):
                if not family_share_ok(by_family, family, atoms_written) or atoms_written >= TARGET_MAX or wrote_job >= job_budget:
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
                if write_atom(
                    family=family,
                    typ=job.get("type") or "text",
                    chunk=chunk,
                    license_=job["license"],
                    source_url=job["source_url"],
                    reception=job.get("reception_layer") or "modern_reception",
                    kind=job.get("correspondence_kind"),
                    existing=existing,
                    by_family=by_family,
                    by_kind=by_kind,
                    type_counts=type_counts,
                    sample_ids=sample_ids,
                ):
                    atoms_written += 1
                    wrote_job += 1
                else:
                    atoms_skipped_dupe += 1
            print(f"  gutenberg wrote={wrote_job}")

    finally:
        if crawler_cm is not None:
            await crawler_cm.__aexit__(None, None, None)

    after = family_counts()
    after_total = sum(after.values())
    by_family_new = dict(by_family)

    for fid, n in sorted(by_family_new.items(), key=lambda x: -x[1]):
        share = (n / atoms_written) if atoms_written else 0.0
        if share > MAX_FAMILY_SHARE + 0.001:
            holds.append({"family_id": fid, "reason": f"NOTE share {share:.1%} of NEW exceeds 25% soft balance"})

    if atoms_written < TARGET_MIN:
        holds.append({
            "reason": f"below TARGET_MIN {TARGET_MIN} (got {atoms_written}) — quality gate preferred over flood",
        })

    family_delta = {fid: after.get(fid, 0) - before.get(fid, 0) for fid in FOCUS_FAMILIES}

    receipt = {
        "run_id": RUN_ID,
        "job_type": "harvest",
        "priority": "E",
        "engine": "crawl4ai",
        "engine_version": "0.9.3",
        "fetch_notes": (
            "urllib archive.sacred-texts.com PD HTML; crawl4ai fallback; "
            "Gutenberg plaintext cache for Blavatsky Key to Theosophy #55618"
        ),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "allowlist": sorted(ALLOW_HOSTS),
        "user_agent": UA,
        "rate_limit_sec": SLEEP_SEC,
        "epistemic": "INFERRED",
        "focus_families": FOCUS_FAMILIES,
        "wave3b_hold": WAVE3B_HOLD,
        "atom_types": ["text", "table", "correspondence", "diagram_desc"],
        "type_counts": dict(type_counts),
        "by_correspondence_kind": dict(by_kind),
        "pages_ok": pages_ok,
        "pages_fail": pages_fail,
        "atoms_written": atoms_written,
        "atoms_skipped_dupe": atoms_skipped_dupe,
        "atoms_skipped_quality": atoms_skipped_quality,
        "by_family_new": by_family_new,
        "before_by_family": {k: before.get(k, 0) for k in FOCUS_FAMILIES},
        "after_by_family": {k: after.get(k, 0) for k in FOCUS_FAMILIES},
        "before_total": before_total,
        "after_total": after_total,
        "family_delta": family_delta,
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
        "no_priority_f": True,
        "atoms_path": str(ATOMS_PATH),
        "backup": str(backup),
        "sample_atom_ids": sample_ids,
        "skipped_hosts": sorted(skipped_hosts),
        "target_range": [TARGET_MIN, TARGET_MAX],
        "max_family_share": MAX_FAMILY_SHARE,
        "proposals": {
            "KEEP": [f for f in FOCUS_FAMILIES if by_family_new.get(f)],
            "HOLD": [h for h in holds if "DROP" not in str(h.get("reason", ""))],
            "DROP": [h for h in holds if "DROP" in str(h.get("reason", ""))],
        },
    }
    # Prefer stable receipt name pattern requested: ingest-priority-e-<run_id>.json
    # RUN_ID already starts with ingest-priority-e-
    receipt_path = RECEIPTS_DIR / f"{RUN_ID}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False))

    lines = [
        f"# Ingest Priority E scoreboard — Wave 3 PD reception",
        f"",
        f"- run_id: `{RUN_ID}`",
        f"- job_type: harvest | priority: **E** | engine: crawl4ai 0.9.3 (+ urllib + Gutenberg cache)",
        f"- timestamp_utc: {receipt['timestamp_utc']}",
        f"- pages_ok: **{pages_ok}** | pages_fail: **{pages_fail}**",
        f"- atoms_written: **{atoms_written}** | dupes: {atoms_skipped_dupe} | quality_skips: {atoms_skipped_quality}",
        f"- before_total: **{before_total}** → after_total: **{after_total}**",
        f"- types: `{dict(type_counts)}`",
        f"- kinds: `{dict(by_kind)}`",
        f"- receipt: `{receipt_path}`",
        f"- backup: `{backup}`",
        f"- script: `/workspace/Athanor/scripts/shadow/athanor/ingest_priority_e.py`",
        f"- chrome_strip: yes | allowlist respected | no Firecrawl | no Wave 3b | no Enochian | no efficacy | no Hub | STOP after E",
        f"",
        f"## Priority E family deltas",
        f"",
        f"| family_id | before | after | delta | % of NEW |",
        f"|---|---:|---:|---:|---:|",
    ]
    for fid in FOCUS_FAMILIES:
        b = before.get(fid, 0)
        a = after.get(fid, 0)
        d = a - b
        pct = (100.0 * d / atoms_written) if atoms_written else 0.0
        lines.append(f"| `{fid}` | {b} | {a} | {d:+d} | {pct:.1f}% |")
    lines += [
        f"",
        f"## Sources used",
        f"",
        f"- sacred-texts: Westcott Historic Lecture (G.D.)",
        f"- sacred-texts: Mathers Kabbalah Unveiled (1887) historical leaves",
        f"- sacred-texts: Waite Book of Ceremonial Magic historical survey (conjuration HOLD)",
        f"- sacred-texts: Blavatsky Isis Unveiled + Secret Doctrine",
        f"- Gutenberg #55618: Blavatsky Key to Theosophy",
        f"- sacred-texts: Leadbeater Textbook of Theosophy (1912); Steiner Theosophy (1910)",
        f"- sacred-texts: Frazer Golden Bough folk-magic anthropological leaves",
        f"- sacred-texts: Grimm Household Tales tradition-prose folk motifs",
        f"- sacred-texts: Spare Focus of Life (1921) + Anathema of Zos (1927) PD-US only",
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
        for fail in failures[:100]:
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
    keep = [f for f in FOCUS_FAMILIES if by_family_new.get(f)]
    lines += [
        f"",
        f"## Propose (never GOLD)",
        f"",
        f"- KEEP: {', '.join(keep) if keep else '(none)'}",
        f"- HOLD: Regardie GD; Grant Cults of the Shadow; modern Spare commentary; TOPY/chaos_late; Pow-Wow efficacy charms; Waite conjuration leaves; Wave 3b; Enochian/Priority F; Spare UK term caveat",
        f"- DROP: SPA chrome-only after strip; HTTP failures; efficacy-framed chunks",
        f"",
        f"## STOP",
        f"",
        f"- Priority E complete for this run. Do **not** start Wave 3b. Priority F = no new Enochian.",
        f"",
    ]
    scoreboard_path = SCOREBOARD_DIR / f"ingest-priority-e-{TS_FILE}.md"
    scoreboard_path.write_text("\n".join(lines) + "\n")

    try:
        shutil.copy2(Path(__file__), SCOREBOARD_DIR / "ingest_priority_e.py")
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
        "by_family_new": by_family_new,
        "family_delta": family_delta,
        "receipt": str(receipt_path),
        "scoreboard": str(scoreboard_path),
        "backup": str(backup),
    }
    print("\n=== SUMMARY ===")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
