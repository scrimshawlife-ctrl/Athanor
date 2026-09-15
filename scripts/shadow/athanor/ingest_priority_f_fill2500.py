#!/usr/bin/env python3
"""ATHANOR-INGEST Priority F — fill harvest to ≥3000 raw corpus atoms.

Thin/underfilled families first (neoplatonism, goetia_catalog historical,
alchemy_lab, jyotish_anchors, hebrew_bible_magical, grimoire_other,
mystery_cults, buddhism_esoteric_pd, solomonic), then deepen other
non-Enochian families under ~80 when PD seeds exist.

Local SoT only. No Firecrawl, no Wave 3b harvest, no Enochian flood,
no HF upload, no git-commit of atoms. Balance: no family > 25% of NEW.
epistemic=INFERRED; efficacy always null; propose KEEP/HOLD/DROP only.
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
CACHE_DIR = SCOREBOARD_DIR / "cache-f"
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
FAMILY_SOFT_CAP = 60  # soft per-family NEW this run (~40–60)
TARGET_CORPUS = 3000  # stop when total atoms ≥ this
TARGET_MIN = 600
TARGET_MAX = 850  # hard cap on NEW this run
HOST_FAIL_SKIP = 2
MAX_FAMILY_SHARE = 0.25

FOCUS_FAMILIES = [
    "neoplatonism",
    "goetia_catalog",
    "alchemy_lab",
    "jyotish_anchors",
    "hebrew_bible_magical",
    "grimoire_other",
    "mystery_cults",
    "buddhism_esoteric_pd",
    "solomonic",
    "islamic_occult_pd",
    "veda_upanishad_pd",
    "tantra_hist_pd",
    "mesoamerica",
    "folk_magic_pd",
    "theosophy_pd",
    "golden_dawn_hist",
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
RUN_ID = f"ingest-priority-f-fill3000-{RUN_TS}-{uuid.uuid4().hex[:8]}"
TS_FILE = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
BACKUP_NAME = f"atoms.pre-ingest-f-{RUN_TS}.jsonl"

MIRROR_HOST = "https://archive.sacred-texts.com"
CANON_HOST = "https://sacred-texts.com"

# ---------------------------------------------------------------------------
# Keywords
# ---------------------------------------------------------------------------
NEO_KW = [
    "plotinus", "ennead", "plato", "soul", "intellect", "one", "nous", "being",
    "emanation", "form", "matter", "virtue", "beauty", "contemplation", "nature",
    "principle", "unity", "good", "hypostasis", "mackenna", "neoplaton",
]
GOETIA_KW = [
    "spirit", "goetia", "solomon", "seal", "sigil", "demon", "office", "rank",
    "legion", "duke", "king", "marquis", "president", "earl", "lesser key",
    "lemegeton", "mathers", "crowley", "catalog", "description", "appears",
]
ALCHEMY_LAB_KW = [
    "alchemy", "alchemical", "mercury", "sulphur", "salt", "furnace", "vessel",
    "distill", "calcination", "putrefaction", "coagulation", "elixir", "stone",
    "antimony", "gold", "silver", "process", "operation", "laboratory", "fire",
    "water", "earth", "air", "tincture", "vitriol", "solution", "fixation",
]
JYOTISH_KW = [
    "hindu", "astrology", "planet", "zodiac", "sign", "horoscope", "nakshatra",
    "solar", "lunar", "jupiter", "saturn", "mars", "mercury", "venus", "rahu",
    "ketu", "ascendant", "yogi", "jyotish", "house", "transit", "birth",
    "capricorn", "aquarius", "pisces", "aries", "taurus", "gemini", "cancer",
    "leo", "virgo", "libra", "scorpio", "sagittarius",
]
HEBREW_MAG_KW = [
    "hebrew", "bible", "jewish", "magic", "magical", "amulet", "angel", "name",
    "divine", "tetragrammaton", "kabbalah", "qabalah", "talisman", "psalm",
    "superstition", "demon", "incantation", "sefer", "yetzirah", "letter",
    "trachtenberg", "bible", "moses", "solomon", "holy", "scripture",
]
GRIMOIRE_KW = [
    "grimoire", "magic", "magical", "spirit", "angel", "seal", "talisman",
    "pentacle", "ceremony", "book", "solomon", "moses", "arbatel", "heptameron",
    "magus", "barrett", "abramelin", "waite", "historical", "manuscript",
]
MYSTERY_KW = [
    "mystery", "mysteries", "mithra", "mithras", "eleusis", "eleusinian",
    "initiation", "cult", "rite", "demeter", "persephone", "orpheus", "orphic",
    "dionysus", "isis", "attis", "cybele", "temple", "initiate", "sacra",
]
BUD_ESO_KW = [
    "buddha", "buddhist", "mahayana", "sutra", "lotus", "tibet", "tantra",
    "mysticism", "doctrine", "bodhisattva", "nirvana", "dharma", "mantra",
    "diamond", "prajna", "emptiness", "school", "system", "historical",
    "schlagintweit", "esoteric", "description", "worship", "literature",
]
SOLOMONIC_KW = [
    "solomon", "key", "pentacle", "spirit", "angel", "seal", "conjuration",
    "circle", "planetary", "hour", "day", "magic", "magical", "manuscript",
    "mathers", "historical", "book", "king", "operation", "instrument",
]
ISLAMIC_KW = [
    "arab", "arabic", "islam", "islamic", "muslim", "sufi", "kindi", "albumasar",
    "picatrix", "talisman", "occult", "astrology", "philosophy", "science",
    "brethren", "basra", "alchemy", "magic", "jinn", "ghayat", "translator",
]
VEDA_KW = [
    "veda", "vedic", "upanishad", "brahman", "atman", "agni", "indra", "soma",
    "rig", "yajur", "sama", "atharva", "mantra", "sacrifice", "hymn", "rishi",
    "chandogya", "katha", "mundaka", "brihad", "prana", "om", "muller", "sbe",
]
TANTRA_KW = [
    "tantra", "shakti", "shakta", "shiva", "devi", "kali", "prakriti", "brahman",
    "mantra", "yantra", "chakra", "kundalini", "woodroffe", "avalon", "shastra",
    "mahanirvana", "historical", "veda", "dharma", "sakti", "goddess", "stotra",
]
MESO_KW = [
    "maya", "aztec", "mexica", "yucatan", "nahuatl", "huitzilopochtli", "tlaloc",
    "katun", "ahau", "chilam", "balam", "quetzalcoatl", "mesoamerica",
    "calendar", "glyph", "temple", "priest", "hymn", "brinton", "roys", "codex",
]
FOLK_KW = [
    "magic", "magical", "folk", "witch", "witchcraft", "charm", "taboo",
    "spirit", "tree", "king", "priest", "ritual", "custom", "tradition",
    "sympathetic", "contagious", "frazer", "grimm", "fairy", "tale",
    "spell", "superstition", "peasant", "europe", "folklore", "soul",
]
THEOS_KW = [
    "theosophy", "blavatsky", "secret doctrine", "isis", "adept", "occult",
    "mahatma", "atma", "buddhi", "manas", "astral", "plane", "reincarnation",
    "karma", "root race", "stanzas", "dzyan", "logos", "cosmic", "evolution",
    "esoteric", "leadbeater", "wisdom", "doctrine", "philosophy", "symbol",
]
GD_KW = [
    "golden", "dawn", "hermetic", "westcott", "mathers", "waite", "order",
    "kabbalah", "qabalah", "sephiroth", "hermes", "rosicrucian", "occult",
    "adept", "temple", "cipher", "ritual", "ceremony", "magic", "magical",
    "grade", "neophyte", "introduction", "historical", "manuscript",
]

HOLD_STATIC = [
    {"url_pattern": "sacred-texts.com/book/", "reason": "HOLD Rowe/Achadian modern /book/ essays"},
    {"family_id": "enochian", "reason": "HOLD — no new Enochian harvest (overweight)"},
    {"note": "Wave 3b families — PROPOSAL ONLY; do not harvest", "family_ids": WAVE3B_HOLD},
    {"url": "https://sacred-texts.com/astro/hba/hba16.htm", "reason": "HOLD/DROP — efficacy/results framing"},
    {"url": "https://sacred-texts.com/bud/ettt/index.htm", "reason": "HOLD — Musés 1961 copyright / practice manuals"},
    {"note": "goetia conjuration/summon UX leaves — HOLD; catalog description only", "paths": [
        "/grim/lks/lks28.htm", "/grim/lks/lks29.htm", "/grim/lks/lks30.htm",
        "/grim/bcm/bcm51.htm", "/grim/bcm/bcm61.htm", "/grim/bcm/bcm63.htm",
    ]},
    {"note": "PA Dutch operational charm leaves — HOLD efficacy", "paths": [
        "/ame/pow/pow003.htm", "/ame/pow/pow012.htm", "/ame/pow/pow016.htm",
    ]},
    {"note": "tantra ritual-formation leaves — HOLD living practice frames", "paths": [
        "/tantra/maha/maha05.htm", "/tantra/maha/maha06.htm", "/tantra/maha/maha07.htm",
        "/tantra/maha/maha09.htm", "/tantra/maha/maha10.htm", "/tantra/maha/maha11.htm",
        "/tantra/maha/maha13.htm", "/tantra/maha/maha14.htm",
    ]},
]

LICENSE_NOTES = [
    "Mackenna Plotinus Enneads — PD-US (INFERRED)",
    "Mathers/Crowley Lesser Key historical catalog leaves — PD-US reception (INFERRED); summon UX HOLD",
    "Classical alchemy lab/process tracts on sacred-texts — PD (INFERRED)",
    "Trachtenberg Jewish Magic and Superstition chapters — PD-US scholarly (INFERRED)",
    "No Firecrawl; Crawl4AI 0.9.3 + urllib mirror; efficacy=null; epistemic=INFERRED",
]


def mh(*paths: str) -> list[str]:
    return [f"{MIRROR_HOST}{p}" for p in paths]


def plotinus_urls() -> list[str]:
    # Prefer tracts not already heavily used (known: 011,012,013,021,031,156,274,429)
    nums = [
        14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30,
        32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
        55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130,
        140, 150, 155, 160, 165, 170, 180, 190, 200, 210, 220, 230, 240, 250,
        260, 270, 280, 290, 300, 320, 340, 360, 380, 400, 420, 440, 460, 480,
        500, 520, 540, 560, 580, 600, 620, 640, 660, 680, 700,
    ]
    return mh(*[f"/cla/plotenn/enn{n:03d}.htm" for n in nums])


# ---------------------------------------------------------------------------
# HTML harvest plan (balanced soft_caps; prefer thin families first)
# ---------------------------------------------------------------------------
HTML_PLAN: list[dict[str, Any]] = [
    # ---- neoplatonism ----
    {
        "family_id": "neoplatonism",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "text",
        "correspondence_kind": "plotinus-enneads",
        "urls": plotinus_urls(),
        "soft_cap": 60,
        "keywords": NEO_KW,
        "dens_min": 0.05,
    },
    {
        "family_id": "neoplatonism",
        "license": "public-domain",
        "reception_layer": "historical_commentary",
        "type": "text",
        "correspondence_kind": "classical-mystery-neoplatonist-adjacent",
        "urls": mh("/cla/demeter.htm", "/cla/aurelmed.htm"),
        "soft_cap": 12,
        "keywords": NEO_KW + MYSTERY_KW,
        "dens_min": 0.04,
    },
    # ---- goetia_catalog (historical catalog ONLY) ----
    {
        "family_id": "goetia_catalog",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "correspondence",
        "correspondence_kind": "goetia-spirit-catalog",
        "urls": mh(
            "/grim/lks/lks04.htm", "/grim/lks/lks05.htm", "/grim/lks/lks06.htm",
            "/grim/lks/lks07.htm", "/grim/lks/lks08.htm", "/grim/lks/lks09.htm",
            "/grim/lks/lks10.htm", "/grim/lks/lks11.htm", "/grim/lks/lks12.htm",
            "/grim/lks/lks13.htm", "/grim/lks/lks14.htm", "/grim/lks/lks15.htm",
            "/grim/lks/lks16.htm", "/grim/lks/lks17.htm", "/grim/lks/lks18.htm",
            "/grim/lks/lks19.htm", "/grim/lks/lks20.htm", "/grim/lks/lks21.htm",
            "/grim/lks/lks22.htm", "/grim/lks/lks23.htm", "/grim/lks/lks24.htm",
            "/grim/lks/lks25.htm", "/grim/lks/lks26.htm", "/grim/lks/lks27.htm",
            "/grim/lks/lks00.htm",
        ),
        "soft_cap": 55,
        "keywords": GOETIA_KW,
        "dens_min": 0.06,
        "require_any": ["spirit", "seal", "solomon", "goetia", "duke", "king", "marquis", "president", "earl", "legion"],
    },
    # ---- alchemy_lab ----
    {
        "family_id": "alchemy_lab",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "text",
        "correspondence_kind": "alchemy-lab-process",
        "urls": mh(
            "/alc/hortulan.htm", "/alc/antimony.htm", "/alc/kellystn.htm",
            "/alc/mass.htm", "/alc/philadel.htm", "/alc/rbacon2.htm",
            "/alc/cc/cc01.htm", "/alc/cc/cc02.htm", "/alc/cc/cc03.htm",
            "/alc/cc/cc04.htm", "/alc/cc/cc05.htm", "/alc/cc/cc06.htm",
            "/alc/cc/cc07.htm", "/alc/cc/cc08.htm", "/alc/cc/cc11.htm",
            "/alc/cc/cc13.htm", "/alc/cc/cc14.htm", "/alc/cc/cc15.htm",
            "/alc/cc/cc17.htm", "/alc/cc/cc18.htm", "/alc/cc/cc19.htm",
            "/alc/cc/cc21.htm", "/alc/cc/cc23.htm",
            "/alc/hm1/hm100.htm", "/alc/hm1/hm101.htm", "/alc/hm1/hm102.htm",
            "/alc/hm1/hm103.htm", "/alc/hm1/hm105.htm", "/alc/hm1/hm107.htm",
            "/alc/hm1/hm108.htm", "/alc/hm1/hm109.htm", "/alc/hm1/hm111.htm",
            "/alc/hm1/hm112.htm", "/alc/hm1/hm114.htm",
            "/alc/arr/arr01.htm", "/alc/arr/arr02.htm", "/alc/arr/arr03.htm",
            "/alc/arr/arr04.htm", "/alc/arr/arr05.htm", "/alc/arr/arr06.htm",
            "/alc/arr/arr07.htm", "/alc/arr/arr08.htm", "/alc/arr/arr09.htm",
            "/alc/arr/arr10.htm", "/alc/arr/arr11.htm", "/alc/arr/arr12.htm",
            "/alc/arr/arr16.htm", "/alc/arr/arr17.htm", "/alc/arr/arr18.htm",
        ),
        "soft_cap": 55,
        "keywords": ALCHEMY_LAB_KW,
        "dens_min": 0.06,
    },
    # ---- jyotish_anchors ----
    {
        "family_id": "jyotish_anchors",
        "license": "public-domain",
        "reception_layer": "historical_commentary",
        "type": "correspondence",
        "correspondence_kind": "hindu-zodiac-anchor",
        "urls": mh(
            "/astro/hba/hba00.htm", "/astro/hba/hba01.htm", "/astro/hba/hba02.htm",
            "/astro/hba/hba17.htm",
            # reuse body pages only if prior run soft-capped early; hash-idempotent
            "/astro/hba/hba03.htm", "/astro/hba/hba04.htm", "/astro/hba/hba05.htm",
            "/astro/hba/hba06.htm", "/astro/hba/hba07.htm", "/astro/hba/hba08.htm",
            "/astro/hba/hba09.htm", "/astro/hba/hba10.htm", "/astro/hba/hba11.htm",
            "/astro/hba/hba12.htm", "/astro/hba/hba13.htm", "/astro/hba/hba14.htm",
            "/astro/hba/hba15.htm",
        ),
        "soft_cap": 40,
        "keywords": JYOTISH_KW,
        "dens_min": 0.07,
        "require_any": ["hindu", "planet", "sign", "zodiac", "astrology", "birth", "nakshatra", "rahu", "ketu"],
    },
    # ---- hebrew_bible_magical ----
    {
        "family_id": "hebrew_bible_magical",
        "license": "public-domain",
        "reception_layer": "historical_commentary",
        "type": "text",
        "correspondence_kind": "jewish-magic-superstition",
        "urls": mh(
            "/jud/jms/jms00.htm", "/jud/jms/jms01.htm", "/jud/jms/jms02.htm",
            "/jud/jms/jms03.htm", "/jud/jms/jms04.htm", "/jud/jms/jms05.htm",
            "/jud/jms/jms06.htm", "/jud/jms/jms07.htm", "/jud/jms/jms08.htm",
            "/jud/jms/jms09.htm", "/jud/jms/jms12.htm", "/jud/jms/jms13.htm",
            "/jud/jms/jms14.htm", "/jud/jms/jms15.htm", "/jud/jms/jms16.htm",
            "/jud/jms/jms17.htm", "/jud/jms/jms18.htm", "/jud/jms/jms19.htm",
            "/jud/jms/jms20.htm", "/jud/jms/jms21.htm", "/jud/jms/jms22.htm",
            "/jud/jms/jms23.htm", "/jud/jms/jms24.htm", "/jud/jms/jms25.htm",
            "/jud/yetzirah.htm",
        ),
        "soft_cap": 55,
        "keywords": HEBREW_MAG_KW,
        "dens_min": 0.05,
    },
    # ---- grimoire_other ----
    {
        "family_id": "grimoire_other",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "text",
        "correspondence_kind": "grimoire-other-hist",
        "urls": mh(
            "/grim/magus/ma100.htm", "/grim/magus/ma101.htm", "/grim/magus/ma102.htm",
            "/grim/magus/ma103.htm", "/grim/magus/ma104.htm", "/grim/magus/ma106.htm",
            "/grim/magus/ma107.htm", "/grim/magus/ma108.htm", "/grim/magus/ma109.htm",
            "/grim/magus/ma110.htm", "/grim/magus/ma111.htm", "/grim/magus/ma112.htm",
            "/grim/magus/ma113.htm", "/grim/magus/ma114.htm", "/grim/magus/ma115.htm",
            "/grim/moses6/m604.htm", "/grim/moses6/m605.htm", "/grim/moses6/m606.htm",
            "/grim/moses6/m607.htm",
            "/grim/moses7/m700.htm", "/grim/moses7/m701.htm", "/grim/moses7/m703.htm",
            "/grim/moses7/m704.htm", "/grim/moses7/m705.htm", "/grim/moses7/m708.htm",
            "/grim/moses7/m709.htm", "/grim/moses7/m710.htm", "/grim/moses7/m711.htm",
            "/grim/moses7/m712.htm", "/grim/moses7/m714.htm", "/grim/moses7/m715.htm",
            "/grim/bcm/bcm01.htm", "/grim/bcm/bcm02.htm", "/grim/bcm/bcm10.htm",
            "/grim/bcm/bcm11.htm", "/grim/bcm/bcm14.htm", "/grim/bcm/bcm15.htm",
            "/grim/bcm/bcm16.htm", "/grim/bcm/bcm17.htm", "/grim/bcm/bcm20.htm",
            "/grim/bcm/bcm21.htm", "/grim/bcm/bcm22.htm", "/grim/bcm/bcm23.htm",
        ),
        "soft_cap": 50,
        "keywords": GRIMOIRE_KW,
        "dens_min": 0.05,
    },
    # ---- mystery_cults ----
    {
        "family_id": "mystery_cults",
        "license": "public-domain",
        "reception_layer": "historical_commentary",
        "type": "text",
        "correspondence_kind": "mithra-eleusis",
        "urls": mh(
            "/cla/mom/mom00.htm", "/cla/mom/mom01.htm", "/cla/mom/mom02.htm",
            "/cla/mom/mom03.htm", "/cla/mom/mom07.htm", "/cla/mom/mom08.htm",
            "/cla/mom/mom09.htm", "/cla/mom/mom10.htm", "/cla/mom/mom11.htm",
            "/cla/ebm/ebm00.htm", "/cla/ebm/ebm01.htm", "/cla/ebm/ebm02.htm",
            "/cla/ebm/ebm03.htm", "/cla/ebm/ebm04.htm", "/cla/ebm/ebm05.htm",
            "/cla/ebm/ebm06.htm", "/cla/ebm/ebm07.htm", "/cla/ebm/ebm08.htm",
            "/cla/ebm/ebm09.htm", "/cla/ebm/ebm10.htm", "/cla/ebm/ebm11.htm",
            "/cla/ebm/ebm12.htm",
            "/cla/demeter.htm",
        ),
        "soft_cap": 50,
        "keywords": MYSTERY_KW,
        "dens_min": 0.05,
    },
    # ---- buddhism_esoteric_pd ----
    {
        "family_id": "buddhism_esoteric_pd",
        "license": "public-domain",
        "reception_layer": "historical_commentary",
        "type": "text",
        "correspondence_kind": "buddhist-esoteric-description",
        "urls": mh(
            "/bud/bit/bit00.htm", "/bud/bit/bit01.htm", "/bud/bit/bit02.htm",
            "/bud/bit/bit03.htm", "/bud/bit/bit04.htm", "/bud/bit/bit05.htm",
            "/bud/bit/bit12.htm", "/bud/bit/bit13.htm", "/bud/bit/bit14.htm",
            "/bud/bit/bit15.htm", "/bud/bit/bit16.htm", "/bud/bit/bit17.htm",
            "/bud/bit/bit18.htm", "/bud/bit/bit19.htm", "/bud/bit/bit20.htm",
            "/bud/lotus/lot04.htm", "/bud/lotus/lot06.htm", "/bud/lotus/lot07.htm",
            "/bud/lotus/lot08.htm", "/bud/lotus/lot09.htm", "/bud/lotus/lot11.htm",
            "/bud/lotus/lot12.htm", "/bud/lotus/lot13.htm", "/bud/lotus/lot14.htm",
            "/bud/lotus/lot16.htm", "/bud/lotus/lot17.htm", "/bud/lotus/lot18.htm",
            "/bud/lotus/lot19.htm", "/bud/lotus/lot20.htm", "/bud/lotus/lot21.htm",
            "/bud/sbe49/sbe4900.htm", "/bud/sbe49/sbe4901.htm", "/bud/sbe49/sbe4903.htm",
            "/bud/sbe49/sbe4904.htm", "/bud/sbe49/sbe4905.htm", "/bud/sbe49/sbe4906.htm",
            "/bud/sbe49/sbe4907.htm", "/bud/sbe49/sbe4908.htm", "/bud/sbe49/sbe4910.htm",
            "/bud/sbe49/sbe4911.htm", "/bud/sbe49/sbe4912.htm", "/bud/sbe49/sbe4915.htm",
        ),
        "soft_cap": 50,
        "keywords": BUD_ESO_KW,
        "dens_min": 0.06,
        "description_only": True,
    },
    # ---- solomonic ----
    {
        "family_id": "solomonic",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "text",
        "correspondence_kind": "greater-key-hist",
        "urls": mh(
            "/grim/kos/kos00.htm", "/grim/kos/kos01.htm", "/grim/kos/kos02.htm",
            "/grim/kos/kos11.htm", "/grim/kos/kos12.htm", "/grim/kos/kos14.htm",
            "/grim/kos/kos15.htm", "/grim/kos/kos16.htm", "/grim/kos/kos17.htm",
            "/grim/kos/kos18.htm", "/grim/kos/kos19.htm", "/grim/kos/kos20.htm",
            "/grim/kos/kos21.htm", "/grim/kos/kos22.htm", "/grim/kos/kos24.htm",
            "/grim/kos/kos25.htm", "/grim/kos/kos26.htm", "/grim/kos/kos27.htm",
            "/grim/kos/kos28.htm", "/grim/kos/kos29.htm", "/grim/kos/kos30.htm",
            "/grim/kos/kos31.htm", "/grim/kos/kos32.htm", "/grim/kos/kos33.htm",
            "/grim/kos/kos34.htm", "/grim/kos/kos35.htm",
            "/grim/kos/kos44.htm", "/grim/kos/kos45.htm",
        ),
        "soft_cap": 45,
        "keywords": SOLOMONIC_KW,
        "dens_min": 0.05,
    },
    # ---- islamic_occult_pd deepen ----
    {
        "family_id": "islamic_occult_pd",
        "license": "public-domain",
        "reception_layer": "historical_commentary",
        "type": "text",
        "correspondence_kind": "arabic-philosophy-occult",
        "urls": mh(
            "/isl/hpi/hpi00.htm", "/isl/hpi/hpi01.htm", "/isl/hpi/hpi02.htm",
            "/isl/hpi/hpi03.htm", "/isl/hpi/hpi04.htm", "/isl/hpi/hpi05.htm",
            "/isl/hpi/hpi06.htm", "/isl/hpi/hpi08.htm", "/isl/hpi/hpi09.htm",
            "/isl/hpi/hpi10.htm", "/isl/hpi/hpi11.htm", "/isl/hpi/hpi15.htm",
            "/isl/hpi/hpi16.htm", "/isl/hpi/hpi17.htm", "/isl/hpi/hpi18.htm",
            "/isl/hpi/hpi19.htm", "/isl/hpi/hpi20.htm", "/isl/hpi/hpi21.htm",
            "/isl/ath/ath00.htm", "/isl/ath/ath01.htm", "/isl/ath/ath02.htm",
            "/isl/ath/ath05.htm", "/isl/ath/ath07.htm", "/isl/ath/ath09.htm",
            "/isl/ath/ath10.htm", "/isl/ath/ath11.htm", "/isl/ath/ath12.htm",
            "/isl/ath/ath13.htm", "/isl/ath/ath14.htm", "/isl/ath/ath15.htm",
            "/sym/bot/bot13.htm",
        ),
        "soft_cap": 45,
        "keywords": ISLAMIC_KW,
        "dens_min": 0.05,
    },
    # ---- veda_upanishad_pd deepen ----
    {
        "family_id": "veda_upanishad_pd",
        "license": "public-domain",
        "reception_layer": "primary_pd",
        "type": "text",
        "correspondence_kind": "upanishad-sbe",
        "urls": mh(
            "/hin/sbe01/sbe01014.htm", "/hin/sbe01/sbe01016.htm", "/hin/sbe01/sbe01018.htm",
            "/hin/sbe01/sbe01019.htm", "/hin/sbe01/sbe01021.htm", "/hin/sbe01/sbe01025.htm",
            "/hin/sbe01/sbe01035.htm", "/hin/sbe01/sbe01045.htm", "/hin/sbe01/sbe01055.htm",
            "/hin/sbe15/sbe15005.htm", "/hin/sbe15/sbe15006.htm", "/hin/sbe15/sbe15008.htm",
            "/hin/sbe15/sbe15009.htm", "/hin/sbe15/sbe15011.htm", "/hin/sbe15/sbe15012.htm",
            "/hin/sbe15/sbe15014.htm", "/hin/sbe15/sbe15015.htm", "/hin/sbe15/sbe15018.htm",
            "/hin/sbe32/sbe3201.htm", "/hin/sbe32/sbe3202.htm", "/hin/sbe32/sbe3203.htm",
            "/hin/sbe32/sbe3205.htm", "/hin/sbe32/sbe3210.htm", "/hin/sbe32/sbe3215.htm",
            "/hin/sbe32/sbe3220.htm", "/hin/sbe32/sbe3225.htm", "/hin/sbe32/sbe3230.htm",
            "/hin/rigveda/rv02112.htm", "/hin/rigveda/rv04051.htm", "/hin/rigveda/rv05083.htm",
        ),
        "soft_cap": 45,
        "keywords": VEDA_KW,
        "dens_min": 0.05,
    },
    # ---- tantra_hist_pd deepen (historical only) ----
    {
        "family_id": "tantra_hist_pd",
        "license": "public-domain",
        "reception_layer": "historical_commentary",
        "type": "text",
        "correspondence_kind": "tantra-historical",
        "urls": mh(
            "/tantra/maha/maha01.htm", "/tantra/maha/maha02.htm", "/tantra/maha/maha03.htm",
            "/tantra/maha/maha04.htm", "/tantra/maha/maha08.htm", "/tantra/maha/maha12.htm",
            "/tantra/sas/sas02.htm", "/tantra/sas/sas03.htm", "/tantra/sas/sas04.htm",
            "/tantra/sas/sas05.htm", "/tantra/sas/sas06.htm", "/tantra/sas/sas08.htm",
            "/tantra/sas/sas09.htm", "/tantra/sas/sas10.htm",
            "/tantra/htg/htg01.htm", "/tantra/htg/htg02.htm", "/tantra/htg/htg03.htm",
        ),
        "soft_cap": 40,
        "keywords": TANTRA_KW,
        "dens_min": 0.06,
    },
    # ---- mesoamerica deepen ----
    {
        "family_id": "mesoamerica",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "text",
        "correspondence_kind": "maya-chilam-balam",
        "urls": mh(
            "/nam/maya/cbc/cbc00.htm", "/nam/maya/cbc/cbc01.htm", "/nam/maya/cbc/cbc02.htm",
            "/nam/maya/cbc/cbc03.htm", "/nam/maya/cbc/cbc04.htm", "/nam/maya/cbc/cbc07.htm",
            "/nam/maya/cbc/cbc09.htm", "/nam/maya/cbc/cbc10.htm", "/nam/maya/cbc/cbc11.htm",
            "/nam/maya/cbc/cbc12.htm", "/nam/maya/cbc/cbc13.htm", "/nam/maya/cbc/cbc14.htm",
            "/nam/maya/cbc/cbc15.htm", "/nam/maya/cbc/cbc16.htm", "/nam/maya/cbc/cbc17.htm",
            "/nam/maya/cbc/cbc18.htm", "/nam/maya/cbc/cbc19.htm", "/nam/maya/cbc/cbc20.htm",
            "/nam/maya/cbc/cbc21.htm", "/nam/maya/cbc/cbc22.htm",
        ),
        "soft_cap": 40,
        "keywords": MESO_KW,
        "dens_min": 0.05,
    },
    # ---- folk_magic_pd deepen ----
    {
        "family_id": "folk_magic_pd",
        "license": "public-domain",
        "reception_layer": "historical_commentary",
        "type": "text",
        "correspondence_kind": "frazer-golden-bough",
        "urls": mh(
            "/pag/frazer/gb00304.htm", "/pag/frazer/gb00400.htm", "/pag/frazer/gb00501.htm",
            "/pag/frazer/gb00600.htm", "/pag/frazer/gb00901.htm", "/pag/frazer/gb00902.htm",
            "/pag/frazer/gb01000.htm", "/pag/frazer/gb01500.htm", "/pag/frazer/gb01801.htm",
            "/pag/frazer/gb01802.htm", "/pag/frazer/gb01803.htm", "/pag/frazer/gb01901.htm",
            "/pag/frazer/gb01902.htm", "/pag/frazer/gb01903.htm", "/pag/frazer/gb01904.htm",
            "/pag/frazer/gb01905.htm", "/pag/frazer/gb00101.htm", "/pag/frazer/gb00200.htm",
            "/neu/grimm/ht03.htm", "/neu/grimm/ht04.htm", "/neu/grimm/ht05.htm",
            "/neu/grimm/ht07.htm", "/neu/grimm/ht08.htm", "/neu/grimm/ht09.htm",
            "/neu/grimm/ht10.htm", "/neu/grimm/ht12.htm", "/neu/grimm/ht13.htm",
        ),
        "soft_cap": 40,
        "keywords": FOLK_KW,
        "dens_min": 0.05,
    },
    # ---- theosophy_pd deepen ----
    {
        "family_id": "theosophy_pd",
        "license": "public-domain",
        "reception_layer": "modern_reception",
        "type": "text",
        "correspondence_kind": "blavatsky-isis-unveiled",
        "urls": mh(
            "/the/iu/iu001.htm", "/the/iu/iu002.htm", "/the/iu/iu003.htm",
            "/the/iu/iu004.htm", "/the/iu/iu005.htm", "/the/iu/iu006.htm",
            "/the/iu/iu007.htm", "/the/iu/iu008.htm", "/the/iu/iu009.htm",
            "/the/iu/iu010.htm", "/the/iu/iu011.htm", "/the/iu/iu012.htm",
            "/the/iu/iu013.htm", "/the/iu/iu014.htm",
            "/the/iu/iu100.htm", "/the/iu/iu101.htm", "/the/iu/iu102.htm",
            "/the/iu/iu103.htm", "/the/iu/iu104.htm", "/the/iu/iu105.htm",
            "/the/sd/sd1-0-pr.htm", "/the/sd/sd1-1-01.htm", "/the/sd/sd1-1-02.htm",
            "/the/sd/sd1-1-03.htm", "/the/sd/sd1-1-04.htm", "/the/sd/sd1-1-05.htm",
            "/the/tot/chap03.htm", "/the/tot/chap04.htm", "/the/tot/chap05.htm",
            "/the/tot/chap06.htm", "/the/tot/chap07.htm", "/the/tot/chap08.htm",
        ),
        "soft_cap": 40,
        "keywords": THEOS_KW,
        "dens_min": 0.05,
    },
    # ---- golden_dawn_hist deepen (PD only) ----
    {
        "family_id": "golden_dawn_hist",
        "license": "public-domain",
        "reception_layer": "modern_reception",
        "type": "text",
        "correspondence_kind": "mathers-kabbalah-unveiled-hist",
        "urls": mh(
            "/jud/tku/tku01.htm", "/jud/tku/tku05.htm", "/jud/tku/tku06.htm",
            "/jud/tku/tku07.htm", "/jud/tku/tku08.htm", "/jud/tku/tku09.htm",
            "/jud/tku/tku10.htm", "/jud/tku/tku11.htm", "/jud/tku/tku12.htm",
            "/jud/tku/tku13.htm", "/jud/tku/tku14.htm", "/jud/tku/tku15.htm",
            "/jud/tku/tku16.htm", "/jud/tku/tku17.htm", "/jud/tku/tku18.htm",
            "/jud/tku/tku20.htm", "/jud/tku/tku22.htm", "/jud/tku/tku24.htm",
            "/jud/tku/tku26.htm", "/jud/tku/tku28.htm", "/jud/tku/tku30.htm",
            "/grim/bcm/bcm03.htm", "/grim/bcm/bcm04.htm", "/grim/bcm/bcm07.htm",
        ),
        "soft_cap": 40,
        "keywords": GD_KW,
        "dens_min": 0.05,
    },
]

print("PLAN jobs", len(HTML_PLAN), "urls", sum(len(j["urls"]) for j in HTML_PLAN))

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



def load_existing_source_urls() -> set[str]:
    urls: set[str] = set()
    if not ATOMS_PATH.exists():
        return urls
    with ATOMS_PATH.open() as f:
        for line in f:
            try:
                obj = json.loads(line)
                u = obj.get("source_url") or ""
                if u:
                    urls.add(u)
                    urls.add(canon_source_url(u))
            except json.JSONDecodeError:
                continue
    return urls


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
    """Skip operational/efficacy/summon UX framing; keep historical access language."""
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
        r"(?i)\bhow to evoke\b",
        r"(?i)\bto call forth the spirit\b",
        r"(?i)\brecite the following conjuration\b",
    ]
    hits = sum(1 for p in bad if re.search(p, text))
    if hits >= 1 and not any(
        w in low for w in ("history", "historical", "manuscript", "century", "translation", "chapter", "doctrine", "described", "catalogue", "catalog", "office is", "his office")
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
    if family_id == "goetia_catalog":
        base["operational"] = False
        base["catalog_only"] = True
    if family_id in ("folk_magic_pd", "golden_dawn_hist", "theosophy_pd"):
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
    known_urls = load_existing_source_urls()
    print(f"run_id={RUN_ID} existing_hashes={len(existing)} known_urls={len(known_urls)} before_total={before_total}")
    print(f"TARGET_CORPUS={TARGET_CORPUS} TARGET_NEW=[{TARGET_MIN},{TARGET_MAX}]")
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
    atoms_skipped_known_url = 0
    by_family: dict[str, int] = defaultdict(int)
    by_kind: dict[str, int] = defaultdict(int)
    sample_ids: list[str] = []
    pages_ok = 0
    pages_fail = 0
    host_fail_streak: dict[str, int] = defaultdict(int)
    skipped_hosts: set[str] = set()
    license_notes = list(LICENSE_NOTES)
    type_counts: Counter = Counter()

    def corpus_reached() -> bool:
        return (before_total + atoms_written) >= TARGET_CORPUS

    def stop_new() -> bool:
        return atoms_written >= TARGET_MAX or corpus_reached()

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
        for job in HTML_PLAN:
            if stop_new():
                holds.append({"reason": f"stop — corpus>={TARGET_CORPUS} or NEW>={TARGET_MAX}"})
                break
            family = job["family_id"]
            if family == "enochian" or family in WAVE3B_HOLD:
                holds.append({"family_id": family, "reason": "HOLD — blocked family"})
                continue
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
                if stop_new() or by_family[family] >= FAMILY_SOFT_CAP or wrote_job >= job_budget:
                    break
                if not family_share_ok(by_family, family, atoms_written):
                    holds.append({"family_id": family, "reason": "balance stop — would exceed ~25% of NEW"})
                    break
                # HOLD path checks
                path = urlparse(url).path or ""
                if "/book/" in path:
                    holds.append({"url": url, "reason": "HOLD Rowe/Achadian /book/"})
                    continue
                if any(path.endswith(p) or path.endswith(p.split('/')[-1]) for h in HOLD_STATIC for p in (h.get("paths") or []) if False):
                    pass
                hold_paths = set()
                for h in HOLD_STATIC:
                    for p in h.get("paths") or []:
                        hold_paths.add(p)
                if any(path.endswith(hp) or path == hp for hp in hold_paths):
                    holds.append({"url": url, "reason": "HOLD listed path"})
                    continue

                canon = canon_source_url(url)
                # Skip URL only when family already has atoms from that exact canon URL
                # (still allow re-fetch if prior run soft-capped; hashes gate dupes)
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
                    "source_url_canon": canon,
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
                if dens < dens_min * 0.40:
                    print(f"    skip page low dens={dens:.3f}")
                    atoms_skipped_quality += 1
                    continue

                wrote_page = 0
                for chunk in chunk_paragraphs(text, min_c=MIN_TABLE_ATOM if typ == "table" else MIN_ATOM):
                    if by_family[family] >= FAMILY_SOFT_CAP or stop_new() or wrote_job >= job_budget:
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
                        "source_url": canon,
                        "epistemic": "INFERRED",
                        "content_hash": chash,
                        "lens_hints": lens_for(family, typ, kind),
                        "harvest_run": RUN_ID,
                        "reception_layer": reception,
                        "efficacy": None,
                    }
                    with ATOMS_PATH.open("a") as f:
                        f.write(json.dumps(atom, ensure_ascii=False) + "\n")
                    existing.add(chash)
                    known_urls.add(canon)
                    atoms_written += 1
                    by_family[family] += 1
                    by_kind[kind or "?"] += 1
                    type_counts[atom["type"]] += 1
                    wrote_page += 1
                    wrote_job += 1
                    if len(sample_ids) < 20:
                        sample_ids.append(aid)
                print(f"    prose={len(text)} wrote={wrote_page} dens={dens:.3f} job_total={wrote_job} corpus~={before_total+atoms_written}")

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

    if after_total < TARGET_CORPUS:
        holds.append({
            "reason": f"below TARGET_CORPUS {TARGET_CORPUS} (got {after_total}) — seeds exhausted or quality gates",
        })
    if atoms_written < TARGET_MIN:
        holds.append({
            "reason": f"below TARGET_MIN NEW {TARGET_MIN} (got {atoms_written})",
        })

    family_delta = {fid: after.get(fid, 0) - before.get(fid, 0) for fid in FOCUS_FAMILIES}

    receipt = {
        "run_id": RUN_ID,
        "job_type": "harvest",
        "priority": "F",
        "goal": "fill3000",
        "engine": "crawl4ai",
        "engine_version": "0.9.3",
        "fetch_notes": "urllib archive.sacred-texts.com PD HTML; crawl4ai fallback; no Firecrawl",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "allowlist": sorted(ALLOW_HOSTS),
        "user_agent": UA,
        "rate_limit_sec": SLEEP_SEC,
        "epistemic": "INFERRED",
        "efficacy": None,
        "focus_families": FOCUS_FAMILIES,
        "atom_types": ["text", "table", "correspondence", "diagram_desc"],
        "type_counts": dict(type_counts),
        "by_correspondence_kind": dict(by_kind),
        "pages_ok": pages_ok,
        "pages_fail": pages_fail,
        "atoms_written": atoms_written,
        "atoms_skipped_dupe": atoms_skipped_dupe,
        "atoms_skipped_quality": atoms_skipped_quality,
        "atoms_skipped_known_url": atoms_skipped_known_url,
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
        "target_corpus": TARGET_CORPUS,
        "target_range_new": [TARGET_MIN, TARGET_MAX],
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
        f"# Ingest Priority F scoreboard — fill3000",
        f"",
        f"- run_id: `{RUN_ID}`",
        f"- job_type: harvest | priority: **F** | goal: **fill3000** | engine: crawl4ai 0.9.3 (+ urllib)",
        f"- timestamp_utc: {receipt['timestamp_utc']}",
        f"- pages_ok: **{pages_ok}** | pages_fail: **{pages_fail}**",
        f"- atoms_written: **{atoms_written}** | dupes: {atoms_skipped_dupe} | quality_skips: {atoms_skipped_quality}",
        f"- before_total: **{before_total}** → after_total: **{after_total}** (target ≥{TARGET_CORPUS})",
        f"- types: `{dict(type_counts)}`",
        f"- kinds: `{dict(by_kind)}`",
        f"- receipt: `{receipt_path}`",
        f"- backup: `{backup}`",
        f"",
        f"## Per-family NEW",
        f"",
        f"| family_id | before | after | delta | % of NEW |",
        f"|---|---:|---:|---:|---:|",
    ]
    for fid in FOCUS_FAMILIES:
        delta = family_delta.get(fid, 0)
        share = (delta / atoms_written * 100) if atoms_written else 0.0
        lines.append(
            f"| {fid} | {before.get(fid, 0)} | {after.get(fid, 0)} | **{delta}** | {share:.1f}% |"
        )
    lines += [
        f"",
        f"## HOLD / DROP notes (proposals only — no settle)",
        f"",
    ]
    for h in holds[:40]:
        lines.append(f"- {h}")
    if len(holds) > 40:
        lines.append(f"- … +{len(holds)-40} more in receipt")
    lines += [
        f"",
        f"## FAILED (sample)",
        f"",
    ]
    for f in failures[:25]:
        lines.append(f"- {f}")
    if len(failures) > 25:
        lines.append(f"- … +{len(failures)-25} more in receipt")
    lines += [
        f"",
        f"## Hard locks honored",
        f"",
        f"- no Firecrawl / no Enochian flood / no Wave 3b harvest / no HF upload / no git-commit atoms",
        f"- Crawl4AI 0.9.3 from Hyperlex venv; UA `{UA}`; ≤1 req / {SLEEP_SEC}s / host; robots.txt",
        f"- chrome strip via `athanor.chrome.strip_chrome`; epistemic=INFERRED; efficacy=null",
        f"- balance soft-cap ≤25% NEW; family soft_cap={FAMILY_SOFT_CAP}",
        f"",
    ]
    scoreboard_path = SCOREBOARD_DIR / f"ingest-priority-f-fill3000-{TS_FILE}.md"
    scoreboard_path.write_text("\n".join(lines) + "\n")
    print("\n=== DONE ===")
    print("atoms_written", atoms_written)
    print("after_total", after_total)
    print("receipt", receipt_path)
    print("scoreboard", scoreboard_path)
    print("by_family_new", dict(by_family_new))


if __name__ == "__main__":
    asyncio.run(main())
