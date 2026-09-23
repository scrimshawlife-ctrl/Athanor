#!/usr/bin/env python3
"""Deepen Athanor corpus: Enochian/Casaubon + Wave 1 families via Crawl4AI 0.9.3."""
from __future__ import annotations

import asyncio
import hashlib
import json
import re
import subprocess
import sys
import urllib.request
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig

HOME = Path.home()
# Unreviewed harvests are candidates, never automatically admitted to retrieval.
ATOMS_PATH = HOME / ".athanor" / "staging" / "legacy-harvest" / "candidates.jsonl"
RECEIPTS_DIR = HOME / ".athanor" / "receipts"
SCOREBOARD_DIR = Path("/workspace/athanor-harvest")
ATOMS_PATH.parent.mkdir(parents=True, exist_ok=True)
RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
SCOREBOARD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWLIST = {"sacred-texts.com", "www.sacred-texts.com", "archive.org"}
UA = "AthanorCorpusBot/0.1 (+research; deepen harvest; contact: local)"
SLEEP_SEC = 1.6
MIN_ATOM = 800
MAX_ATOM = 2000
MIN_PAGE_CHARS = 200

RUN_TS = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
RUN_ID = f"deepen-{RUN_TS}-{uuid.uuid4().hex[:8]}"
TS_FILE = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

WAVE0_ENOCH_BOOKS = {
    "https://sacred-texts.com/book/an-essay-on-the-pronunciation-of-enochian",
    "https://sacred-texts.com/book/eso-enoch-callench",
    "https://sacred-texts.com/book/an-enochian-dictionary",
    "https://sacred-texts.com/book/gematria-values-of-the-enochian-characters",
    "https://sacred-texts.com/book/the-first-key-an-analysis-of-the-first-enochian-call-or-key",
    "https://sacred-texts.com/book/the-second-key-experiments-with-the-second-enochian-call-or-key",
    "https://sacred-texts.com/book/enochian-magick",
}

ENOCH_BOOK_SEEDS = [
    "https://sacred-texts.com/book/enochian-rituals",
    "https://sacred-texts.com/book/book-of-the-seniors",
    "https://sacred-texts.com/book/the-lotus-of-power-ritual",
    "https://sacred-texts.com/book/advorpt-90th-region-in-the-progression-of-the-aethyrs",
    "https://sacred-texts.com/book/a-vision-of-the-square-t-of-ismt-of-the-fiery-lesser-angle-of-the-earth-tablet",
    "https://sacred-texts.com/book/enochian-temples-contruction-of-the-macrocosmic-enochian-temples",
    "https://sacred-texts.com/book/the-lower-temple-construction-of-the-microcosmic-temples",
    "https://sacred-texts.com/book/the-temple-of-fire-consecrating-the-temple-of-the-fire-tablet",
    "https://sacred-texts.com/book/the-cacodemons-invoking-the-cacodemons-with-the-temples",
    "https://sacred-texts.com/book/the-abyss-experience-generating-the-abyss-experience",
    "https://sacred-texts.com/book/the-ritual-of-the-hexagram-an-experimental-enochian-ritual",
    "https://sacred-texts.com/book/divine-creation-and-intiation-the-process-of-aeonic-emanations",
    "https://sacred-texts.com/book/the-paths-a-brief-listing-of-the-achadian-paths",
    "https://sacred-texts.com/book/the-land-medieval-social-structure-and-the-achadian-tree",
    "https://sacred-texts.com/book/the-book-of-the-archer-using-the-astrological-chart-as-a-lamen",
    "https://sacred-texts.com/book/the-zodiacal-round-the-precessional-sequence-as-steps-in-creativity",
    "https://sacred-texts.com/book/some-notes-on-gematria-in-liber-al-random-musings-on-liber-al",
]

PLAN: list[dict[str, Any]] = [
    {
        "seed": "https://archive.org/download/truefaithfulrela00deej/truefaithfulrela00deej_djvu.txt",
        "family_id": "enochian",
        "license": "public-domain (Casaubon 1659 True & Faithful Relation)",
        "max_children": 0,
        "path_prefix": None,
        "child_glob": None,
        "title_note": None,
        "archive_txt_direct": True,
        "byte_start": 100_000,
        "byte_end": 700_000,
        "label": "casaubon_txt_segment",
    },
    {
        "seed": "https://sacred-texts.com/eso/enoch/index.htm",
        "family_id": "enochian",
        "license": "PD / archive claim (sacred-texts Enochian)",
        "max_children": 0,
        "path_prefix": "/eso/enoch/",
        "child_glob": None,
        "title_note": None,
        "explicit_urls": ENOCH_BOOK_SEEDS,
        "explicit_cap": 15,
        "skip_urls": WAVE0_ENOCH_BOOKS,
        "label": "enochian_book_children",
    },
    {
        "seed": "https://sacred-texts.com/egy/dmp/",
        "family_id": "egypt_magical",
        "license": "PD edition (Griffith/Thompson Demotic Magical Papyrus)",
        "max_children": 0,
        "path_prefix": "/egy/dmp/",
        "child_glob": None,
        "title_note": None,
        "explicit_urls": [
            "https://sacred-texts.com/egy/dmp/dmp02.htm",
            "https://sacred-texts.com/egy/dmp/dmp03.htm",
            "https://sacred-texts.com/egy/dmp/dmp04.htm",
            "https://sacred-texts.com/egy/dmp/dmp05.htm",
            "https://sacred-texts.com/egy/dmp/dmp06.htm",
            "https://sacred-texts.com/book/the-demotic-magical-papyrus-of-london-and-leiden/read/col-i",
            "https://sacred-texts.com/book/the-demotic-magical-papyrus-of-london-and-leiden/read/col-ii",
            "https://sacred-texts.com/book/the-demotic-magical-papyrus-of-london-and-leiden/read/col-iii",
            "https://sacred-texts.com/book/the-demotic-magical-papyrus-of-london-and-leiden/read/col-iv",
            "https://sacred-texts.com/book/the-demotic-magical-papyrus-of-london-and-leiden/read/col-v",
            "https://sacred-texts.com/book/the-demotic-magical-papyrus-of-london-and-leiden/read/introduction",
            "https://sacred-texts.com/book/the-demotic-magical-papyrus-of-london-and-leiden/read/preface",
        ],
        "explicit_cap": 12,
        "skip_urls": {
            "https://sacred-texts.com/egy/dmp/",
            "https://sacred-texts.com/egy/dmp/index.htm?chaptersPage=2",
            "https://sacred-texts.com/egy/dmp/index.htm?chaptersPage=3",
            "https://sacred-texts.com/egy/dmp/dmp00.htm",
            "https://sacred-texts.com/egy/dmp/dmp01.htm",
        },
        "label": "egypt_magical_deeper",
    },
    {
        "seed": "https://sacred-texts.com/ane/enuma.htm",
        "family_id": "mesopotamia",
        "license": "PD (King Enuma Elish / Seven Tablets)",
        "max_children": 4,
        "path_prefix": "/ane/",
        "child_glob": None,
        "title_note": None,
        "explicit_urls": [
            "https://sacred-texts.com/ane/enuma.htm",
            "https://sacred-texts.com/ane/stc/index.htm",
            "https://sacred-texts.com/ane/stc/stc03.htm",
            "https://sacred-texts.com/ane/gilgdelu.htm",
            "https://sacred-texts.com/ane/eog/eog01.htm",
        ],
        "explicit_cap": 5,
        "label": "mesopotamia",
    },
    {
        "seed": "https://sacred-texts.com/jud/jms/jms10.htm",
        "family_id": "hebrew_bible_magical",
        "license": "sacred-texts host (Trachtenberg Jewish Magic — Bible-in-magic reception; light harvest)",
        "max_children": 2,
        "path_prefix": "/jud/jms/",
        "child_glob": r"jms0[89]|jms1[01]",
        "title_note": None,
        "explicit_urls": [
            "https://sacred-texts.com/jud/jms/jms10.htm",
            "https://sacred-texts.com/jud/jms/jms11.htm",
            "https://sacred-texts.com/jud/jms/index.htm",
        ],
        "explicit_cap": 3,
        "label": "hebrew_bible_magical_light",
    },
    {
        "seed": "https://sacred-texts.com/chr/ps/index.htm",
        "family_id": "coptic_gnostic",
        "license": "PD (Mead Pistis Sophia)",
        "max_children": 6,
        "path_prefix": "/chr/ps/",
        "child_glob": r"ps0.*\.htm",
        "title_note": None,
        "explicit_urls": [
            "https://sacred-texts.com/chr/ps/index.htm",
            "https://sacred-texts.com/chr/ps/ps003.htm",
            "https://sacred-texts.com/chr/ps/ps004.htm",
            "https://sacred-texts.com/chr/ps/ps005.htm",
            "https://sacred-texts.com/chr/ps/ps006.htm",
            "https://sacred-texts.com/chr/ps/ps007.htm",
            "https://sacred-texts.com/chr/ps/ps008.htm",
        ],
        "explicit_cap": 7,
        "label": "coptic_gnostic",
    },
    {
        "seed": "https://sacred-texts.com/astro/ptb/index.htm",
        "family_id": "astrology_west",
        "license": "PD (Ashmand Tetrabiblos)",
        "max_children": 8,
        "path_prefix": "/astro/ptb/",
        "child_glob": r"ptb0.*\.htm",
        "title_note": None,
        "explicit_urls": [
            "https://sacred-texts.com/astro/ptb/index.htm",
            "https://sacred-texts.com/astro/ptb/ptb00.htm",
            "https://sacred-texts.com/astro/ptb/ptb02.htm",
            "https://sacred-texts.com/astro/ptb/ptb04.htm",
            "https://sacred-texts.com/astro/ptb/ptb05.htm",
            "https://sacred-texts.com/astro/ptb/ptb06.htm",
            "https://sacred-texts.com/astro/ptb/ptb07.htm",
            "https://sacred-texts.com/astro/ptb/ptb08.htm",
            "https://sacred-texts.com/astro/ptb/ptb31.htm",
        ],
        "explicit_cap": 9,
        "label": "astrology_west_tetrabiblos",
    },
    {
        "seed": "https://sacred-texts.com/cla/plotenn/index.htm",
        "family_id": "neoplatonism",
        "license": "PD (Mackenna Enneads)",
        "max_children": 8,
        "path_prefix": "/cla/plotenn/",
        "child_glob": r"enn0.*\.htm",
        "title_note": None,
        "explicit_urls": [
            "https://sacred-texts.com/cla/plotenn/index.htm",
            "https://sacred-texts.com/cla/plotenn/enn011.htm",
            "https://sacred-texts.com/cla/plotenn/enn012.htm",
            "https://sacred-texts.com/cla/plotenn/enn013.htm",
            "https://sacred-texts.com/cla/plotenn/enn021.htm",
            "https://sacred-texts.com/cla/plotenn/enn031.htm",
            "https://sacred-texts.com/cla/plotenn/enn156.htm",
            "https://sacred-texts.com/cla/plotenn/enn274.htm",
            "https://sacred-texts.com/cla/plotenn/enn429.htm",
        ],
        "explicit_cap": 9,
        "label": "neoplatonism_plotinus",
    },
]

def host_ok(url: str) -> bool:
    try:
        h = urlparse(url).hostname or ""
        return h.lower() in ALLOWLIST
    except Exception:
        return False


def normalize_url(url: str) -> str:
    u = url.strip()
    if "#" in u:
        u = u.split("#", 1)[0]
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


def clean_markdown(md: str) -> str:
    if not md:
        return ""
    lines = []
    skip_patterns = [
        r"^\[?\s*(Home|Index|Sacred Texts|Next|Previous|Contents)\s*\]?",
        r"^---+",
        r"^===+",
    ]
    for line in md.splitlines():
        s = line.strip()
        if any(re.match(p, s, re.IGNORECASE) for p in skip_patterns):
            if re.match(r"^---+", s) or re.match(r"^===+", s):
                lines.append("")
            continue
        if re.match(r"^\[.+\]\(.+\)$", s) and len(s) < 80:
            continue
        lines.append(line)
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_ocr_txt(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[■□▪▫]+", "", text)
    text = re.sub(r"[ \t]{2,}", "  ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_paragraphs(text: str, min_c: int = MIN_ATOM, max_c: int = MAX_ATOM) -> list[str]:
    if not text or len(text) < MIN_PAGE_CHARS:
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
        if len(buf) >= min_c or (not chunks and len(buf) >= MIN_PAGE_CHARS):
            chunks.append(buf)
        elif chunks:
            if len(chunks[-1]) + 2 + len(buf) <= max_c + 400:
                chunks[-1] = chunks[-1] + "\n\n" + buf
            else:
                chunks.append(buf)
    return chunks


def extract_same_host_links(
    html_or_md: str, base_url: str, path_prefix: str | None, child_glob: str | None
) -> list[str]:
    links: list[str] = []
    patterns = [
        r"\[([^\]]*)\]\(([^)]+)\)",
        r'href=["\']([^"\']+)["\']',
    ]
    found: list[str] = []
    for pat in patterns:
        for m in re.finditer(pat, html_or_md or ""):
            href = m.group(2) if m.lastindex and m.lastindex >= 2 else m.group(1)
            found.append(href)
    seen = set()
    for href in found:
        if not href or href.startswith(("mailto:", "javascript:", "#")):
            continue
        abs_u = normalize_url(urljoin(base_url, href))
        if abs_u in seen:
            continue
        parsed = urlparse(abs_u)
        if (parsed.hostname or "").lower() not in ALLOWLIST:
            continue
        if path_prefix:
            if not parsed.path.startswith(path_prefix):
                continue
            if abs_u.rstrip("/") == base_url.rstrip("/"):
                continue
            if not re.search(r"\.(htm|html)/?$", parsed.path, re.IGNORECASE) and not parsed.path.endswith("/"):
                if "." in Path(parsed.path).name:
                    continue
        if child_glob:
            name = Path(parsed.path).name
            if not re.search(child_glob, name, re.IGNORECASE):
                continue
        seen.add(abs_u)
        links.append(abs_u)
    return links


def lens_for(family_id: str, title_note: str | None) -> dict:
    if family_id == "goetia_catalog" or title_note == "historical_catalog":
        return {"historical": True, "symbolic": True, "operational": False}
    if family_id in (
        "enochian", "hermetic", "alchemy_lab", "kabbalah_pd", "egypt_magical",
        "mesopotamia", "hebrew_bible_magical", "coptic_gnostic", "astrology_west", "neoplatonism",
    ):
        return {"historical": True, "symbolic": True, "operational": False}
    return {"historical": True, "symbolic": True}


def fetch_url_urllib(url: str, timeout: int = 120) -> dict[str, Any]:
    if not host_ok(url):
        return {"ok": False, "url": url, "error": "host not allowlisted", "status": None, "text": "", "html": "", "md": ""}
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            status = getattr(resp, "status", 200)
            text = None
            for enc in ("utf-8", "latin-1", "cp1252"):
                try:
                    text = raw.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            if text is None:
                text = raw.decode("utf-8", errors="replace")
            return {"ok": True, "url": url, "error": None, "status": status, "text": text, "html": "", "md": text}
    except Exception as e:
        return {"ok": False, "url": url, "error": str(e), "status": None, "text": "", "html": "", "md": ""}


async def crawl_url(crawler: AsyncWebCrawler, url: str) -> dict[str, Any]:
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
        blob = (md + "\n" + html[:5000]).lower()
        if "cloudflare" in blob and (
            "attention required" in blob or "cf-browser-verification" in blob or "just a moment" in blob
        ):
            return {"ok": False, "url": url, "error": "Cloudflare block", "status": status, "md": "", "html": html}
        if not ok:
            return {"ok": False, "url": url, "error": err or "crawl failed", "status": status, "md": md, "html": html}
        return {"ok": True, "url": url, "error": None, "status": status, "md": md, "html": html}
    except Exception as e:
        return {"ok": False, "url": url, "error": str(e), "status": None, "md": "", "html": ""}

async def main() -> None:
    before = family_counts()
    before_total = sum(before.values())
    existing = load_existing_hashes()
    print(f"run_id={RUN_ID} existing_hashes={len(existing)} before_total={before_total}")
    print("before_by_family=", dict(before))

    try:
        browser_cfg = BrowserConfig(headless=True, verbose=False)
    except TypeError:
        browser_cfg = BrowserConfig(headless=True)

    urls_attempted: list[dict] = []
    failures: list[dict] = []
    atoms_written = 0
    atoms_skipped_dupe = 0
    by_family: dict[str, int] = {}
    sample_ids: list[str] = []
    pages_ok = 0
    enoch_book_pages = 0

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        for job in PLAN:
            seed = job["seed"]
            family = job["family_id"]
            license_ = job["license"]
            title_note = job.get("title_note")
            label = job.get("label") or family
            print(f"\n=== {label}: {family} ===")

            if job.get("archive_txt_direct"):
                url = seed
                print(f"  urllib fetch {url}")
                result = fetch_url_urllib(url)
                urls_attempted.append({
                    "url": url, "family_id": family, "ok": result["ok"],
                    "status": result.get("status"), "error": result.get("error"), "mode": "urllib_txt",
                })
                await asyncio.sleep(SLEEP_SEC)
                if not result["ok"]:
                    failures.append({"url": url, "error": result.get("error"), "status": result.get("status")})
                    print(f"    FAILED: {result.get('error')}")
                    continue
                pages_ok += 1
                full = clean_ocr_txt(result.get("text") or result.get("md") or "")
                start = int(job.get("byte_start") or 0)
                end = int(job.get("byte_end") or len(full))
                md = full[start:end]
                print(f"    full={len(full)} chars; segment[{start}:{end}] -> {len(md)}")
                if len(md) < MIN_PAGE_CHARS:
                    print("    skip short segment")
                    continue
                chunks = chunk_paragraphs(md)
                print(f"    -> {len(chunks)} chunks")
                for chunk in chunks:
                    ch = content_hash(chunk)
                    if ch in existing:
                        atoms_skipped_dupe += 1
                        continue
                    aid = atom_id_for(family, ch)
                    atom = {
                        "atom_id": aid, "family_id": family, "type": "text", "text": chunk,
                        "license": license_, "source_url": url, "epistemic": "INFERRED",
                        "content_hash": ch, "lens_hints": lens_for(family, title_note),
                        "harvest_run": RUN_ID, "segment": f"{start}:{end}",
                    }
                    with ATOMS_PATH.open("a") as f:
                        f.write(json.dumps(atom, ensure_ascii=False) + "\n")
                    existing.add(ch)
                    atoms_written += 1
                    by_family[family] = by_family.get(family, 0) + 1
                    if len(sample_ids) < 5:
                        sample_ids.append(aid)
                continue

            skip_urls = {normalize_url(u) for u in (job.get("skip_urls") or set())}
            explicit = [normalize_url(u) for u in (job.get("explicit_urls") or [])]
            explicit_cap = job.get("explicit_cap")
            queue: list[str] = []
            if explicit:
                added = 0
                for u in explicit:
                    if u in skip_urls:
                        continue
                    if explicit_cap is not None and added >= explicit_cap:
                        break
                    if u not in queue:
                        queue.append(u)
                        added += 1
            else:
                queue = [seed]

            crawled_for_job: set[str] = set()
            children_added = 0
            max_children = job.get("max_children") or 0

            while queue:
                url = normalize_url(queue.pop(0))
                if url in crawled_for_job:
                    continue
                if not host_ok(url):
                    failures.append({"url": url, "error": "host not allowlisted"})
                    continue
                path_l = urlparse(url).path.lower()
                if any(path_l.endswith(ext) for ext in (".pdf", ".epub", ".zip", ".djvu", ".mp3", ".mobi", ".gz")):
                    failures.append({"url": url, "error": "skipped binary extension"})
                    continue

                print(f"  crawl {url}")
                result = await crawl_url(crawler, url)
                crawled_for_job.add(url)
                urls_attempted.append({
                    "url": url, "family_id": family, "ok": result["ok"],
                    "status": result.get("status"), "error": result.get("error"),
                })
                await asyncio.sleep(SLEEP_SEC)

                if not result["ok"]:
                    failures.append({"url": url, "error": result.get("error"), "status": result.get("status")})
                    print(f"    FAILED: {result.get('error')}")
                    continue

                pages_ok += 1
                if family == "enochian" and "/book/" in url:
                    enoch_book_pages += 1

                md = clean_markdown(result["md"] or "")
                if not md and result.get("html"):
                    md = clean_markdown(re.sub(r"<[^>]+>", " ", result["html"]))

                if max_children > 0 and children_added < max_children and (
                    url == seed or url in (job.get("explicit_urls") or [])[:1]
                ):
                    src = (result.get("html") or "") + "\n" + (result.get("md") or "")
                    kids = extract_same_host_links(src, seed, job.get("path_prefix"), job.get("child_glob"))
                    for k in kids:
                        if children_added >= max_children:
                            break
                        if k not in crawled_for_job and k not in queue and k not in skip_urls:
                            queue.append(k)
                            children_added += 1
                    if children_added:
                        print(f"    queued +{children_added} children")

                if len(md) < MIN_PAGE_CHARS:
                    print(f"    skip empty/nav-only ({len(md)} chars)")
                    continue

                if len(md) > 120_000:
                    md = md[:120_000]
                    print("    truncated long text to 120k chars")

                chunks = chunk_paragraphs(md)
                print(f"    text={len(md)} chars -> {len(chunks)} chunks")

                for chunk in chunks:
                    ch = content_hash(chunk)
                    if ch in existing:
                        atoms_skipped_dupe += 1
                        continue
                    aid = atom_id_for(family, ch)
                    atom = {
                        "atom_id": aid, "family_id": family, "type": "text", "text": chunk,
                        "license": license_, "source_url": url, "epistemic": "INFERRED",
                        "content_hash": ch, "lens_hints": lens_for(family, title_note),
                        "harvest_run": RUN_ID,
                    }
                    with ATOMS_PATH.open("a") as f:
                        f.write(json.dumps(atom, ensure_ascii=False) + "\n")
                    existing.add(ch)
                    atoms_written += 1
                    by_family[family] = by_family.get(family, 0) + 1
                    if len(sample_ids) < 5:
                        sample_ids.append(aid)

    after = family_counts()
    after_total = sum(after.values())

    receipt = {
        "run_id": RUN_ID,
        "engine": "crawl4ai",
        "engine_version": "0.9.3",
        "started_note": "Deepen Enochian/Casaubon + Wave 1 expansion",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "allowlist": sorted(ALLOWLIST),
        "atom_count_new": atoms_written,
        "atoms_skipped_dupe": atoms_skipped_dupe,
        "pages_ok": pages_ok,
        "enochian_book_pages_crawled": enoch_book_pages,
        "urls": urls_attempted,
        "failures": failures,
        "by_family_new": by_family,
        "before_by_family": dict(before),
        "after_by_family": dict(after),
        "before_total": before_total,
        "after_total": after_total,
        "atoms_path": str(ATOMS_PATH),
        "user_agent": UA,
        "epistemic_policy": "INFERRED for crawl (do not claim OBSERVED on atoms)",
        "rate_limit_sec": SLEEP_SEC,
        "no_firecrawl": True,
        "no_git_commit": True,
    }
    receipt_path = RECEIPTS_DIR / f"{RUN_ID}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False))

    all_fams = sorted(set(before) | set(after) | set(by_family))
    lines = [
        "# Deepen harvest scoreboard",
        "",
        f"- run_id: `{RUN_ID}`",
        "- engine: crawl4ai 0.9.3 (+ urllib for IA plaintext)",
        f"- timestamp_utc: {receipt['timestamp_utc']}",
        f"- atoms_written (net new): **{atoms_written}**",
        f"- atoms_skipped_dupe: {atoms_skipped_dupe}",
        f"- before_total: {before_total} → after_total: {after_total}",
        f"- pages_ok: {pages_ok}",
        f"- enochian /book/ pages crawled: {enoch_book_pages}",
        f"- failures: {len(failures)}",
        f"- receipt: `{receipt_path}`",
        f"- atoms: `{ATOMS_PATH}`",
        "- allowlist: sacred-texts.com, archive.org",
        "",
        "## Before / After by family_id",
        "",
        "| family_id | before | after | delta |",
        "|---|---:|---:|---:|",
    ]
    for fid in sorted(all_fams, key=lambda x: (-(after.get(x, 0)), x)):
        b = before.get(fid, 0)
        a = after.get(fid, 0)
        lines.append(f"| `{fid}` | {b} | {a} | {a - b:+d} |")
    lines.append("")
    lines.append("## New atoms this run")
    lines.append("")
    for fid, n in sorted(by_family.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"- `{fid}`: {n}")
    lines.append("")
    lines.append("## Sample atom_ids")
    lines.append("")
    for s in sample_ids:
        lines.append(f"- `{s}`")
    lines.append("")
    lines.append("## FAILED URLs")
    lines.append("")
    if not failures:
        lines.append("- (none)")
    else:
        for fail in failures:
            lines.append(f"- {fail.get('url')}: {fail.get('error')}")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Atom epistemic set to INFERRED (crawl harvest).")
    lines.append("- Casaubon deepen uses IA djvu.txt segment beyond wave0 120k window; idempotent by content_hash.")
    lines.append("- Corpus under ~/.athanor/ — not committed to git.")
    lines.append("- No Firecrawl.")
    scoreboard_path = SCOREBOARD_DIR / f"deepen-{TS_FILE}.md"
    scoreboard_path.write_text("\n".join(lines) + "\n")

    summary = {
        "atoms_written": atoms_written,
        "by_family_new": by_family,
        "before_by_family": dict(before),
        "after_by_family": dict(after),
        "before_total": before_total,
        "after_total": after_total,
        "receipt": str(receipt_path),
        "scoreboard": str(scoreboard_path),
        "failures": len(failures),
        "sample_ids": sample_ids,
        "enochian_book_pages": enoch_book_pages,
    }
    # Jev post-filter for high quality (T4-JEV-001 wiring)
    jev_script = Path(__file__).parent / "jev_classify.py"
    if jev_script.exists() and ATOMS_PATH.exists():
        try:
            with ATOMS_PATH.open() as f:
                cand_lines = [line for line in f if line.strip()]
            if cand_lines:
                input_data = "".join(cand_lines)
                proc = subprocess.run(
                    [sys.executable, str(jev_script), "--min-relevance", "0.7"],
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if proc.returncode == 0 and proc.stdout.strip():
                    high_lines = proc.stdout.strip().splitlines()
                    high_path = ATOMS_PATH.with_suffix(".jev_high.jsonl")
                    with high_path.open("w") as f:
                        f.write("\n".join(high_lines) + "\n")
                    print(f"Jev filtered {len(high_lines)} high-quality atoms -> {high_path}")
                    # Optionally, replace candidates with high only for this run
                    # ATOMS_PATH.write_text("\n".join(high_lines) + "\n")
        except Exception as e:
            print(f"Jev filter error: {e}")

    print("\\n==== DONE ====")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
