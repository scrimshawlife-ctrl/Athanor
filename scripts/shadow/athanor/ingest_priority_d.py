#!/usr/bin/env python3
"""ATHANOR-INGEST Priority D — Wave 2 PD families.

Families: veda_upanishad_pd, jyotish_anchors, tantra_hist_pd (historical only),
buddhism_esoteric_pd (description/doctrinal only), iching_daoist (PD deepen),
mesoamerica (sacred-texts PD + Met Open Access object notes).

Local SoT only. No Firecrawl, no Wave 3b, no Enochian flood, no HF upload,
no git-commit of atoms. Balance: no family > 25% of NEW this run.
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
CACHE_DIR = SCOREBOARD_DIR / "cache-d"
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
FAMILY_SOFT_CAP = 70  # prefer ~40–80; hard balance ≤25% NEW
TARGET_MIN = 200
TARGET_MAX = 360
HOST_FAIL_SKIP = 2
MAX_FAMILY_SHARE = 0.25

FOCUS_FAMILIES = [
    "veda_upanishad_pd",
    "jyotish_anchors",
    "tantra_hist_pd",
    "buddhism_esoteric_pd",
    "iching_daoist",
    "mesoamerica",
]

RUN_TS = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
RUN_ID = f"ingest-priority-d-{RUN_TS}-{uuid.uuid4().hex[:8]}"
TS_FILE = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
BACKUP_NAME = f"atoms.pre-ingest-d-{RUN_TS}.jsonl"

MIRROR_HOST = "https://archive.sacred-texts.com"
CANON_HOST = "https://sacred-texts.com"

# ---------------------------------------------------------------------------
# Keywords
# ---------------------------------------------------------------------------
VEDA_KW = [
    "veda", "vedic", "upanishad", "brahman", "atman", "agni", "indra", "soma",
    "rig", "yajur", "sama", "atharva", "mantra", "sacrifice", "hymn", "rishi",
    "chandogya", "katha", "mundaka", "brihad", "svetasvatara", "prana", "om",
    "muller", "sbe", "sanctity", "knowledge", "immortal",
]
JYOTISH_KW = [
    "hindu", "astrology", "planet", "zodiac", "sign", "horoscope", "nakshatra",
    "solar", "lunar", "jupiter", "saturn", "mars", "mercury", "venus", "rahu",
    "ketu", "ascendant", "yogi", "jyotish", "house", "transit", "birth",
    "capricorn", "aquarius", "pisces", "aries", "taurus", "gemini", "cancer",
    "leo", "virgo", "libra", "scorpio", "sagittarius",
]
TANTRA_KW = [
    "tantra", "shakti", "shakta", "shiva", "devi", "kali", "prakriti", "brahman",
    "mantra", "yantra", "chakra", "kundalini", "woodroffe", "avalon", "shastra",
    "mahanirvana", "historical", "veda", "dharma", "sakti", "goddess", "stotra",
]
BUD_ESO_KW = [
    "buddha", "buddhist", "mahayana", "sutra", "lotus", "tibet", "tantra",
    "mysticism", "doctrine", "bodhisattva", "nirvana", "dharma", "mantra",
    "diamond", "prajna", "emptiness", "school", "system", "historical",
    "schlagintweit", "esoteric", "description", "worship", "literature",
]
ICHING_KW = [
    "hexagram", "yi", "king", "line", "trigram", "ch'ien", "khien", "khwan",
    "appendix", "judgment", "image", "legge", "tao", "yin", "yang", "change",
    "oracle", "divination", "figure", "lines", "firm", "yielding",
]
MESO_KW = [
    "maya", "aztec", "mexica", "yucatan", "nahuatl", "huitzilopochtli", "tlaloc",
    "katun", "ahau", "chilam", "balam", "quetzalcoatl", "mexica", "mesoamerica",
    "calendar", "glyph", "temple", "priest", "hymn", "brinton", "roys", "met",
    "culture", "vessel", "relief", "censer", "codex", "itolca", "itzá",
]

HOLD_STATIC = [
    {
        "url": "https://sacred-texts.com/bud/ettt/index.htm",
        "reason": "HOLD — Musés 1961 Esoteric Teachings of the Tibetan Tantra (post-1928 copyright; practice manuals)",
    },
    {
        "url": "https://sacred-texts.com/nam/maya/ybac/index.htm",
        "reason": "HOLD — Gates 1937 Yucatan Before and After the Conquest; renewal-era English translation, no clear non-renewal receipt here",
    },
    {
        "url": "https://sacred-texts.com/nam/maya/mhw/index.htm",
        "reason": "HOLD — Thompson 1950 Maya Hieroglyphic Writing; renewal-era, copyright-unclear for harvest",
    },
    {
        "url": "https://sacred-texts.com/astro/hba/hba16.htm",
        "reason": "HOLD/DROP — HBA 'Rules for Attaining Health, Wealth And Happiness' (efficacy/results framing)",
    },
    {
        "note": "tantra ritual-formation leaves (maha05–07, 09–11, 13–14) — HOLD living/operational initiatory practice frames",
        "paths": [
            "/tantra/maha/maha05.htm",
            "/tantra/maha/maha06.htm",
            "/tantra/maha/maha07.htm",
            "/tantra/maha/maha09.htm",
            "/tantra/maha/maha10.htm",
            "/tantra/maha/maha11.htm",
            "/tantra/maha/maha13.htm",
            "/tantra/maha/maha14.htm",
        ],
    },
    {
        "host": "www.britishmuseum.org",
        "reason": "HOLD — BM object pages errored/unstable this run (HTTP 520); prefer Met OA + sacred-texts PD",
    },
    {"family_id": "enochian", "reason": "HOLD — out of Priority D scope; no Enochian flood"},
    {
        "note": "Wave 3b families — PROPOSAL ONLY; do not harvest",
        "family_ids": ["thelema_pd", "wicca_hist"],
    },
]

def mh(*paths: str) -> list[str]:
    return [f"{MIRROR_HOST}{p}" for p in paths]


# ---------------------------------------------------------------------------
# HTML harvest plan (balanced soft_caps)
# ---------------------------------------------------------------------------
HTML_PLAN: list[dict[str, Any]] = [
    # ---- veda_upanishad_pd ----
    {
        "family_id": "veda_upanishad_pd",
        "license": "public-domain",
        "reception_layer": "primary_pd",
        "type": "text",
        "correspondence_kind": "upanishad-sbe",
        "urls": mh(
            "/hin/sbe01/sbe01010.htm",
            "/hin/sbe01/sbe01012.htm",
            "/hin/sbe01/sbe01013.htm",
            "/hin/sbe01/sbe01015.htm",
            "/hin/sbe01/sbe01017.htm",
            "/hin/sbe01/sbe01020.htm",
            "/hin/sbe01/sbe01030.htm",
            "/hin/sbe01/sbe01040.htm",
            "/hin/sbe01/sbe01050.htm",
            "/hin/sbe01/sbe01060.htm",
            "/hin/sbe15/sbe15002.htm",
            "/hin/sbe15/sbe15003.htm",
            "/hin/sbe15/sbe15004.htm",
            "/hin/sbe15/sbe15007.htm",
            "/hin/sbe15/sbe15010.htm",
            "/hin/sbe15/sbe15016.htm",
            "/hin/sbe15/sbe15020.htm",
        ),
        "soft_cap": 36,
        "keywords": VEDA_KW,
        "dens_min": 0.06,
    },
    {
        "family_id": "veda_upanishad_pd",
        "license": "public-domain",
        "reception_layer": "primary_pd",
        "type": "text",
        "correspondence_kind": "rigveda-hymn",
        "urls": mh(
            "/hin/rigveda/rv01000.htm",
            "/hin/rigveda/rv01001.htm",
            "/hin/rigveda/rv01032.htm",
            "/hin/rigveda/rv01089.htm",
            "/hin/rigveda/rv10090.htm",
            "/hin/rigveda/rv10129.htm",
            "/hin/rigveda/rv02112.htm",
            "/hin/rigveda/rv03062.htm",
            "/hin/rigveda/rv07086.htm",
            "/hin/rigveda/rv09001.htm",
        ),
        "soft_cap": 28,
        "keywords": VEDA_KW,
        "dens_min": 0.05,
    },
    # ---- jyotish_anchors ----
    {
        "family_id": "jyotish_anchors",
        "license": "public-domain",
        "reception_layer": "historical_commentary",
        "type": "correspondence",
        "correspondence_kind": "hindu-zodiac-anchor",
        "urls": mh(
            "/astro/hba/hba03.htm",
            "/astro/hba/hba04.htm",
            "/astro/hba/hba05.htm",
            "/astro/hba/hba06.htm",
            "/astro/hba/hba07.htm",
            "/astro/hba/hba08.htm",
            "/astro/hba/hba09.htm",
            "/astro/hba/hba10.htm",
            "/astro/hba/hba11.htm",
            "/astro/hba/hba12.htm",
            "/astro/hba/hba13.htm",
            "/astro/hba/hba14.htm",
            "/astro/hba/hba15.htm",
        ),
        "soft_cap": 55,
        "keywords": JYOTISH_KW,
        "dens_min": 0.08,
        "require_any": ["hindu", "planet", "sign", "zodiac", "astrology", "birth"],
    },
    # ---- tantra_hist_pd (historical / literary only) ----
    {
        "family_id": "tantra_hist_pd",
        "license": "public-domain",
        "reception_layer": "historical_commentary",
        "type": "text",
        "correspondence_kind": "tantra-historical",
        "urls": mh(
            "/tantra/maha/maha00.htm",
            "/tantra/maha/maha01.htm",
            "/tantra/maha/maha02.htm",
            "/tantra/maha/maha03.htm",
            "/tantra/maha/maha04.htm",
            "/tantra/maha/maha08.htm",
            "/tantra/maha/maha12.htm",
            "/tantra/sas/sas01.htm",
            "/tantra/sas/sas02.htm",
            "/tantra/sas/sas03.htm",
            "/tantra/sas/sas04.htm",
            "/tantra/sas/sas05.htm",
            "/tantra/sas/sas06.htm",
            "/tantra/sas/sas08.htm",
            "/tantra/sas/sas09.htm",
            "/tantra/sas/sas10.htm",
            "/tantra/htg/htg01.htm",
            "/tantra/htg/htg03.htm",
        ),
        "soft_cap": 55,
        "keywords": TANTRA_KW,
        "dens_min": 0.07,
    },
    # ---- buddhism_esoteric_pd (description / doctrinal only) ----
    {
        "family_id": "buddhism_esoteric_pd",
        "license": "public-domain",
        "reception_layer": "historical_commentary",
        "type": "text",
        "correspondence_kind": "buddhist-esoteric-description",
        "urls": mh(
            "/bud/bit/bit06.htm",
            "/bud/bit/bit07.htm",
            "/bud/bit/bit08.htm",
            "/bud/bit/bit09.htm",
            "/bud/bit/bit10.htm",
            "/bud/bit/bit11.htm",
            "/bud/sbe49/sbe4902.htm",
            "/bud/sbe49/sbe4929.htm",
            "/bud/lotus/lot01.htm",
            "/bud/lotus/lot02.htm",
            "/bud/lotus/lot03.htm",
            "/bud/lotus/lot05.htm",
            "/bud/lotus/lot10.htm",
            "/bud/lotus/lot15.htm",
        ),
        "soft_cap": 55,
        "keywords": BUD_ESO_KW,
        "dens_min": 0.07,
        "description_only": True,
    },
    # ---- iching_daoist deepen (prefer new leaves beyond ic01–ic22) ----
    {
        "family_id": "iching_daoist",
        "license": "public-domain",
        "reception_layer": "primary_pd",
        "type": "correspondence",
        "correspondence_kind": "hexagram-judgment",
        "urls": mh(
            "/ich/icintr01.htm",
            "/ich/icintr02.htm",
            "/ich/icintr03.htm",
            "/ich/ic23.htm",
            "/ich/ic24.htm",
            "/ich/ic25.htm",
            "/ich/ic26.htm",
            "/ich/ic27.htm",
            "/ich/ic28.htm",
            "/ich/ic29.htm",
            "/ich/ic30.htm",
            "/ich/ic31.htm",
            "/ich/ic32.htm",
            "/ich/ic33.htm",
            "/ich/ic34.htm",
            "/ich/ic35.htm",
            "/ich/ic36.htm",
            "/ich/ic37.htm",
            "/ich/ic38.htm",
            "/ich/ic39.htm",
            "/ich/ic40.htm",
            "/ich/ic41.htm",
            "/ich/ic42.htm",
            "/ich/ic43.htm",
            "/ich/ic44.htm",
            "/ich/ic45.htm",
            "/ich/ic46.htm",
            "/ich/ic47.htm",
            "/ich/ic48.htm",
            "/ich/ic49.htm",
            "/ich/ic50.htm",
        ),
        "soft_cap": 40,
        "keywords": ICHING_KW,
        "dens_min": 0.05,
    },
    {
        "family_id": "iching_daoist",
        "license": "public-domain",
        "reception_layer": "primary_pd",
        "type": "text",
        "correspondence_kind": "daoist-pd",
        "urls": mh(
            "/tao/sbe39/sbe3902.htm",
            "/tao/sbe39/sbe3903.htm",
            "/tao/tt/tt00.htm",
            "/tao/tt/tt01.htm",
            "/tao/tt/tt02.htm",
            "/tao/ts/ts00.htm",
            "/tao/ycw/ycw00.htm",
            "/tao/ttx/ttx00.htm",
        ),
        "soft_cap": 20,
        "keywords": ICHING_KW + ["tao", "lao", "te", "virtue", "way", "wu wei", "lieh"],
        "dens_min": 0.05,
    },
    # ---- mesoamerica sacred-texts PD ----
    {
        "family_id": "mesoamerica",
        "license": "public-domain",
        "reception_layer": "primary_pd",
        "type": "text",
        "correspondence_kind": "aztec-hymn",
        "urls": mh(
            "/nam/aztec/rva/rva00.htm",
            "/nam/aztec/rva/rva01.htm",
            "/nam/aztec/rva/rva02.htm",
            "/nam/aztec/rva/rva03.htm",
            "/nam/aztec/rva/rva04.htm",
            "/nam/aztec/rva/rva05.htm",
            "/nam/aztec/rva/rva06.htm",
            "/nam/aztec/rva/rva07.htm",
            "/nam/aztec/rva/rva08.htm",
            "/nam/aztec/rva/rva09.htm",
            "/nam/aztec/rva/rva12.htm",
            "/nam/aztec/rva/rva15.htm",
            "/nam/aztec/rva/rva16.htm",
            "/nam/aztec/rva/rva18.htm",
        ),
        "soft_cap": 28,
        "keywords": MESO_KW,
        "dens_min": 0.05,
    },
    {
        "family_id": "mesoamerica",
        "license": "public-domain",
        "reception_layer": "primary_pd",
        "type": "text",
        "correspondence_kind": "maya-chilam-balam",
        "urls": mh(
            "/nam/maya/cbc/cbc05.htm",
            "/nam/maya/cbc/cbc06.htm",
            "/nam/maya/cbc/cbc08.htm",
            "/nam/maya/cbc/cbc10.htm",
            "/nam/maya/cbc/cbc11.htm",
            "/nam/maya/cbc/cbc13.htm",
            "/nam/maya/cbc/cbc14.htm",
            "/nam/maya/cbc/cbc15.htm",
            "/nam/maya/cbc/cbc16.htm",
            "/nam/maya/cbc/cbc17.htm",
            "/nam/maya/cbc/cbc20.htm",
        ),
        "soft_cap": 28,
        "keywords": MESO_KW,
        "dens_min": 0.05,
        "license_note": "Roys 1933 Chilam Balam — sacred-texts asserts US non-renewal PD (INFERRED)",
    },
]

# Met Open Access object IDs (public-domain Mesoamerican; skip non-Meso false positives)
MET_OBJECT_IDS = [
    310542, 310364, 318345, 313256, 313240, 310555, 317760, 718242,
    307599, 307636, 307634, 310472, 310599, 307734, 329077,
]

LICENSE_NOTES = [
    "Max Müller Upanishads SBE 1/15 (1879/1884): public-domain sacred-texts (INFERRED).",
    "Griffith Rig Veda translation (1896): public-domain sacred-texts (INFERRED).",
    "Bhakti Seva, Hindu Book of Astrology (1902): public-domain sacred-texts; efficacy chapter HOLD (INFERRED).",
    "Arthur Avalon / Woodroffe Mahanirvana Tantra + Shakti and Shâkta + Hymns to the Goddess (c.1913–1920): PD historical/literary leaves only; ritual-formation chapters HOLD (INFERRED).",
    "Schlagintweit, Buddhism in Tibet (1863): public-domain historical description (INFERRED).",
    "SBE 49 Buddhist Mahâyâna Texts + SBE 21 Lotus Sutra (Kern): public-domain doctrinal description (INFERRED).",
    "Legge I Ching (SBE 16, 1882) + SBE 39/40 Taoist texts: public-domain deepen (INFERRED).",
    "Brinton Rig Veda Americanus (1890): public-domain (INFERRED).",
    "Roys Book of Chilam Balam of Chumayel (1933): sacred-texts asserts non-renewal → PD-US (INFERRED).",
    "Gates Yucatan (1937) + Thompson Maya Hieroglyphic Writing (1950): HOLD copyright-unclear.",
    "Musés Esoteric Teachings of the Tibetan Tantra (1961): HOLD copyright + practice manuals.",
    "Met Museum Open Access public-domain object metadata: CC0 (INFERRED via isPublicDomain API flag).",
    "British Museum object pages: HOLD (fetch errors this run).",
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
        r"(?i)^hinduism$",
        r"(?i)^buddhism$",
        r"(?i)^taoism$",
        r"(?i)^tantra$",
        r"(?i)^astrology$",
        r"(?i)^native american$",
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
    ]
    hits = sum(1 for p in bad if re.search(p, text))
    if hits >= 1 and not any(
        w in low for w in ("history", "historical", "manuscript", "century", "translation", "chapter", "doctrine", "described")
    ):
        return True
    return False


def is_practice_results_frame(text: str) -> bool:
    """For buddhism_esoteric_pd / tantra: block practice-as-results instructions."""
    low = text.lower()
    patterns = [
        r"(?i)\bdo the following visualization\b",
        r"(?i)\brepeat this mantra\s+\d+\s+times\b",
        r"(?i)\bthe yogi should now\b",
        r"(?i)\bthis sādhana will\b",
        r"(?i)\bthis sadhana will\b",
        r"(?i)\binitiation ritual\b.*\bperform\b",
        r"(?i)\bsix yogas of n[aā]ropa\b.*\binstruction",
        r"(?i)\bguaranteed enlightenment\b",
    ]
    if any(re.search(p, text) for p in patterns):
        # allow if clearly scholarly description of historical practice
        if any(w in low for w in ("schlagintweit", "describes", "according to", "the text states", "historically", "in tibet the")):
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
    if family_id in ("buddhism_esoteric_pd", "tantra_hist_pd"):
        base["operational"] = False
        base["description_only"] = family_id == "buddhism_esoteric_pd"
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
            if "application/json" in ctype:
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
        # short but dense correspondence anchors (zodiac leaves, hymns)
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
    """Cap each family at min(FAMILY_SOFT_CAP, floor(MAX_FAMILY_SHARE * TARGET_MAX)).

    Live % of NEW is checked only in the receipt; sequential harvest cannot
    fairly enforce running share without starving early families.
    """
    per_family_max = min(FAMILY_SOFT_CAP, int(TARGET_MAX * MAX_FAMILY_SHARE))
    return by_family.get(family, 0) < per_family_max


def met_object_to_text(obj: dict[str, Any]) -> str:
    fields = [
        "title", "objectName", "culture", "period", "objectDate", "medium",
        "dimensions", "classification", "department", "creditLine",
        "accessionNumber", "repository", "country", "region", "subregion",
        "excavation", "geographyType", "locale",
    ]
    lines = ["Met Open Access object note (public-domain work; CC0 metadata):"]
    for k in fields:
        v = obj.get(k)
        if v:
            lines.append(f"{k}: {v}")
    # optional gallery-ish strings
    for k, v in obj.items():
        if isinstance(v, str) and v and ("label" in k.lower() or k in ("message", "provenance")):
            if k not in fields:
                lines.append(f"{k}: {v}")
    if obj.get("objectURL"):
        lines.append(f"objectURL: {obj['objectURL']}")
    tags = obj.get("tags") or []
    if tags:
        tag_terms = []
        for t in tags:
            if isinstance(t, dict) and t.get("term"):
                tag_terms.append(t["term"])
            elif isinstance(t, str):
                tag_terms.append(t)
        if tag_terms:
            lines.append("tags: " + ", ".join(tag_terms[:20]))
    return "\n".join(lines).strip()


def meso_culture_ok(obj: dict[str, Any]) -> bool:
    blob = " ".join(
        str(obj.get(k) or "")
        for k in ("culture", "title", "objectName", "region", "country", "department", "classification")
    ).lower()
    needles = [
        "maya", "aztec", "mexica", "toltec", "veracruz", "olmec", "mixtec",
        "zapotec", "teotihuacan", "mesoamerica", "mexico", "guatemala", "honduras",
    ]
    # reject clear non-meso false positives
    if "egypt" in blob or "book of the dead" in blob:
        return False
    return any(n in blob for n in needles)


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
            license_ = job["license"]
            if license_ not in {"public-domain", "pd-us", "cc0", "cc-by"}:
                holds.append({"family_id": family, "reason": f"unclear license {license_}"})
                continue
            if by_family[family] >= FAMILY_SOFT_CAP:
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
                if atoms_written >= TARGET_MAX or by_family[family] >= FAMILY_SOFT_CAP or wrote_job >= job_budget:
                    break
                if not family_share_ok(by_family, family, atoms_written):
                    holds.append({"family_id": family, "reason": "balance stop — would exceed ~25% of NEW"})
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
                    if by_family[family] >= FAMILY_SOFT_CAP or atoms_written >= TARGET_MAX or wrote_job >= job_budget:
                        break
                    if not family_share_ok(by_family, family, atoms_written):
                        break
                    chunk = strip_chrome(chunk).strip()
                    if not accept_chunk(
                        chunk,
                        typ == "table",
                        keywords,
                        dens_min=dens_min,
                        require_any=require_any,
                        description_only=description_only or family == "buddhism_esoteric_pd",
                    ):
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
                    if len(sample_ids) < 18:
                        sample_ids.append(aid)
                print(f"    prose={len(text)} wrote={wrote_page} dens={dens:.3f} job_total={wrote_job}")

        # ---- Met Open Access Mesoamerica object notes ----
        if atoms_written < TARGET_MAX and by_family["mesoamerica"] < FAMILY_SOFT_CAP:
            print("\n=== MET Open Access mesoamerica objects ===")
            wrote_met = 0
            met_budget = 18
            for oid in MET_OBJECT_IDS:
                if atoms_written >= TARGET_MAX or by_family["mesoamerica"] >= FAMILY_SOFT_CAP or wrote_met >= met_budget:
                    break
                if not family_share_ok(by_family, "mesoamerica", atoms_written):
                    holds.append({"family_id": "mesoamerica", "reason": "balance stop — Met would exceed ~25% of NEW"})
                    break
                api_url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}"
                print(f"  fetch {api_url}")
                result = fetch_urllib(api_url)
                urls_attempted.append({
                    "url": api_url,
                    "source_url_canon": api_url,
                    "family_id": "mesoamerica",
                    "kind": "met-oa-object",
                    "ok": result["ok"],
                    "status": result.get("status"),
                    "error": result.get("error"),
                    "mode": "urllib-json",
                })
                await asyncio.sleep(SLEEP_SEC)
                if not result["ok"]:
                    pages_fail += 1
                    failures.append({"url": api_url, "error": result.get("error"), "status": result.get("status")})
                    continue
                try:
                    obj = json.loads(result["body"])
                except json.JSONDecodeError:
                    pages_fail += 1
                    failures.append({"url": api_url, "error": "json decode fail"})
                    continue
                if not obj.get("isPublicDomain"):
                    holds.append({"url": api_url, "reason": "HOLD — Met object not isPublicDomain"})
                    continue
                if not meso_culture_ok(obj):
                    holds.append({"url": api_url, "reason": "DROP — non-Mesoamerican / false-positive Met hit"})
                    continue
                pages_ok += 1
                text = met_object_to_text(obj)
                if len(text) < MIN_TABLE_ATOM:
                    atoms_skipped_quality += 1
                    continue
                chash = content_hash(text)
                if chash in existing:
                    atoms_skipped_dupe += 1
                    continue
                source = obj.get("objectURL") or f"https://www.metmuseum.org/art/collection/search/{oid}"
                aid = atom_id_for("mesoamerica", chash)
                atom = {
                    "atom_id": aid,
                    "family_id": "mesoamerica",
                    "type": "diagram_desc",
                    "text": text,
                    "license": "cc0",
                    "source_url": source,
                    "epistemic": "INFERRED",
                    "content_hash": chash,
                    "lens_hints": lens_for("mesoamerica", "diagram_desc", "met-oa-object"),
                    "harvest_run": RUN_ID,
                    "reception_layer": "museum_oa",
                }
                with ATOMS_PATH.open("a") as f:
                    f.write(json.dumps(atom, ensure_ascii=False) + "\n")
                existing.add(chash)
                atoms_written += 1
                by_family["mesoamerica"] += 1
                by_kind["met-oa-object"] += 1
                type_counts["diagram_desc"] += 1
                wrote_met += 1
                if len(sample_ids) < 18:
                    sample_ids.append(aid)
                print(f"    wrote met {oid} chars={len(text)}")
            print(f"  met wrote_total={wrote_met}")

    finally:
        if crawler_cm is not None:
            await crawler_cm.__aexit__(None, None, None)

    after = family_counts()
    after_total = sum(after.values())
    by_family_new = dict(by_family)

    # balance report
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
        "priority": "D",
        "engine": "crawl4ai",
        "engine_version": "0.9.3",
        "fetch_notes": (
            "urllib archive.sacred-texts.com PD HTML; crawl4ai fallback; "
            "Met collectionapi Open Access JSON for Mesoamerica object notes"
        ),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "allowlist": sorted(ALLOW_HOSTS),
        "user_agent": UA,
        "rate_limit_sec": SLEEP_SEC,
        "epistemic": "INFERRED",
        "focus_families": FOCUS_FAMILIES,
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
        "family_delta": family_delta,
        "urls": urls_attempted,
        "FAILED": failures,
        "HOLD": holds,
        "license_notes": license_notes,
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
        "max_family_share": MAX_FAMILY_SHARE,
        "proposals": {
            "KEEP": [f for f in FOCUS_FAMILIES if by_family_new.get(f)],
            "HOLD": [h for h in holds if "DROP" not in str(h.get("reason", ""))],
            "DROP": [h for h in holds if "DROP" in str(h.get("reason", ""))],
        },
    }
    receipt_path = RECEIPTS_DIR / f"{RUN_ID}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False))

    lines = [
        f"# Ingest Priority D scoreboard — Wave 2 PD families",
        f"",
        f"- run_id: `{RUN_ID}`",
        f"- job_type: harvest | priority: **D** | engine: crawl4ai 0.9.3 (+ urllib + Met OA API)",
        f"- timestamp_utc: {receipt['timestamp_utc']}",
        f"- pages_ok: **{pages_ok}** | pages_fail: **{pages_fail}**",
        f"- atoms_written: **{atoms_written}** | dupes: {atoms_skipped_dupe} | quality_skips: {atoms_skipped_quality}",
        f"- before_total: **{before_total}** → after_total: **{after_total}**",
        f"- types: `{dict(type_counts)}`",
        f"- kinds: `{dict(by_kind)}`",
        f"- receipt: `{receipt_path}`",
        f"- backup: `{backup}`",
        f"- script: `/workspace/Athanor/scripts/shadow/athanor/ingest_priority_d.py`",
        f"- chrome_strip: yes | allowlist respected | no Firecrawl | no Wave 3b | no Enochian | no efficacy | no Hub",
        f"",
        f"## Priority D family deltas",
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
        f"- sacred-texts: Müller Upanishads SBE1/15; Griffith Rig-Veda hymn leaves",
        f"- sacred-texts: Hindu Book of Astrology (1902) zodiac anchors (efficacy ch. HOLD)",
        f"- sacred-texts: Avalon/Woodroffe Mahanirvana + Shakti and Shâkta + Hymns intro (historical leaves)",
        f"- sacred-texts: Schlagintweit Buddhism in Tibet; SBE49/Lotus doctrinal description",
        f"- sacred-texts: Legge I Ching ic23–50 + intros; Taoist PD deepen leaves",
        f"- sacred-texts: Brinton Rig Veda Americanus (1890); Roys Chilam Balam (non-renewal claim)",
        f"- Met Open Access API: Mesoamerican public-domain object metadata (CC0)",
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
        f"- HOLD: ETTT Musés 1961; Gates Yucatan 1937; Thompson MHW 1950; Mahanirvana ritual-formation ch.; HBA efficacy ch.; BM pages; Wave 3b; Enochian",
        f"- DROP: SPA chrome-only after strip; non-Meso Met false positives; HTTP failures",
        f"",
    ]
    scoreboard_path = SCOREBOARD_DIR / f"ingest-priority-d-{TS_FILE}.md"
    scoreboard_path.write_text("\n".join(lines) + "\n")

    try:
        shutil.copy2(Path(__file__), SCOREBOARD_DIR / "ingest_priority_d.py")
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
