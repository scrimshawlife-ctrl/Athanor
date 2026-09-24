#!/usr/bin/env python3
"""Wave 0 Enochian-first harvest for Athanor via Crawl4AI 0.9.3."""
from __future__ import annotations

import asyncio
import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

# Paths
HOME = Path.home()
# Unreviewed harvests are candidates, never automatically admitted to retrieval.
ATOMS_PATH = HOME / ".athanor" / "staging" / "legacy-harvest" / "candidates.jsonl"
RECEIPTS_DIR = HOME / ".athanor" / "receipts"
SCOREBOARD_DIR = Path("/workspace/athanor-harvest")
ATOMS_PATH.parent.mkdir(parents=True, exist_ok=True)
RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
SCOREBOARD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWLIST = {"sacred-texts.com", "www.sacred-texts.com", "archive.org"}
UA = "AthanorCorpusBot/0.1 (+research; Wave0 harvest; contact: local)"
SLEEP_SEC = 1.6
MIN_ATOM = 800
MAX_ATOM = 2000
MIN_PAGE_CHARS = 200  # skip nav-only

RUN_ID = f"wave0-enochian-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
TS_LOCAL = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

# Harvest plan: (seed_url, family_id, license, max_same_host_children, path_prefix_or_None, child_pattern_or_None)
PLAN = [
    {
        "seed": "https://sacred-texts.com/eso/enoch/index.htm",
        "family_id": "enochian",
        "license": "PD / archive claim",
        "max_children": 7,  # + seed = 8 pages cap
        "path_prefix": "/eso/enoch/",
        "child_glob": None,
        "title_note": None,
    },
    {
        "seed": "https://archive.org/details/truefaithfulrela00deej",
        "family_id": "enochian",
        "license": "public-domain (1659)",
        "max_children": 0,
        "path_prefix": None,
        "child_glob": None,
        "title_note": None,
        "archive_item": True,
    },
    {
        "seed": "https://sacred-texts.com/chr/herm/index.htm",
        "family_id": "hermetic",
        "license": "PD (Mead)",
        "max_children": 5,
        "path_prefix": "/chr/herm/",
        "child_glob": r"hermes.*\.htm",
        "title_note": None,
    },
    {
        "seed": "https://sacred-texts.com/alc/emerald.htm",
        "family_id": "alchemy_lab",
        "license": "PD translations",
        "max_children": 0,
        "path_prefix": None,
        "child_glob": None,
        "title_note": None,
    },
    {
        "seed": "https://sacred-texts.com/grim/lks/",
        "family_id": "goetia_catalog",
        "license": "PD Mathers/Crowley ed. claim",
        "max_children": 3,
        "path_prefix": "/grim/lks/",
        "child_glob": None,
        "title_note": "historical_catalog",
    },
    {
        "seed": "https://sacred-texts.com/jud/yetzirah.htm",
        "family_id": "kabbalah_pd",
        "license": "PD",
        "max_children": 0,
        "path_prefix": None,
        "child_glob": None,
        "title_note": None,
    },
    {
        "seed": "https://sacred-texts.com/ich/index.htm",
        "family_id": "iching_daoist",
        "license": "PD (Legge et al.)",
        "max_children": 2,
        "path_prefix": "/ich/",
        "child_glob": None,
        "title_note": None,
    },
    {
        "seed": "https://sacred-texts.com/egy/dmp/",
        "family_id": "egypt_magical",
        "license": "PD edition",
        "max_children": 2,
        "path_prefix": "/egy/dmp/",
        "child_glob": None,
        "title_note": None,
    },
    {
        "seed": "https://sacred-texts.com/neu/poe/",
        "family_id": "runes_eddic",
        "license": "PD",
        "max_children": 1,
        "path_prefix": "/neu/poe/",
        "child_glob": None,
        "title_note": None,
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
    # drop fragments
    if "#" in u:
        u = u.split("#", 1)[0]
    return u


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def atom_id_for(family_id: str, chash: str) -> str:
    return f"{family_id}:{chash[:16]}"


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
    # strip common nav noise lines
    lines = []
    skip_patterns = [
        r"^\[?\s*(Home|Index|Sacred Texts|Next|Previous|Contents)\s*\]?",
        r"^---+",
        r"^===+",
        r"^\s*$",
    ]
    for line in md.splitlines():
        s = line.strip()
        if any(re.match(p, s, re.I) for p in skip_patterns[:3]):
            # keep separators as paragraph breaks sometimes
            if re.match(r"^---+", s) or re.match(r"^===+", s):
                lines.append("")
            continue
        # drop pure link-list short lines that are nav
        if re.match(r"^\[.+\]\(.+\)$", s) and len(s) < 80:
            continue
        lines.append(line)
    text = "\n".join(lines)
    # collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_paragraphs(text: str, min_c: int = MIN_ATOM, max_c: int = MAX_ATOM) -> list[str]:
    """Split at paragraph boundaries into ~800-2000 char atoms."""
    if not text or len(text) < MIN_PAGE_CHARS:
        return []
    paras = re.split(r"\n\s*\n", text)
    paras = [p.strip() for p in paras if p.strip()]
    chunks: list[str] = []
    buf = ""
    for p in paras:
        # if single para is huge, hard-split on sentences
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
                    # buf short; attach even if overshoot slightly, or flush if way over
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
            # merge tiny tail into last if fits
            if len(chunks[-1]) + 2 + len(buf) <= max_c + 400:
                chunks[-1] = chunks[-1] + "\n\n" + buf
            else:
                chunks.append(buf)
    return chunks


def extract_same_host_links(html_or_md: str, base_url: str, path_prefix: str | None, child_glob: str | None) -> list[str]:
    links: list[str] = []
    # from markdown links and hrefs
    patterns = [
        r'\[([^\]]*)\]\(([^)]+)\)',
        r'href=["\']([^"\']+)["\']',
    ]
    found: list[str] = []
    for pat in patterns:
        for m in re.finditer(pat, html_or_md or ""):
            href = m.group(2) if m.lastindex and m.lastindex >= 2 else m.group(1)
            found.append(href)
    base_host = (urlparse(base_url).hostname or "").lower()
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
        # same host preference for sacred-texts children
        if path_prefix:
            if not parsed.path.startswith(path_prefix):
                continue
            # skip the seed itself for children list
            if abs_u.rstrip("/") == base_url.rstrip("/"):
                continue
            # prefer .htm/.html pages
            if not re.search(r"\.(htm|html)/?$", parsed.path, re.I) and not parsed.path.endswith("/"):
                # allow directory indexes
                if "." in Path(parsed.path).name:
                    continue
        if child_glob:
            name = Path(parsed.path).name
            if not re.search(child_glob, name, re.I):
                continue
        seen.add(abs_u)
        links.append(abs_u)
    return links


def lens_for(family_id: str, title_note: str | None) -> dict:
    if family_id == "goetia_catalog" or title_note == "historical_catalog":
        return {"historical": True, "symbolic": True, "operational": False}
    if family_id in ("enochian", "hermetic", "alchemy_lab", "kabbalah_pd"):
        return {"historical": True, "symbolic": True, "operational": False}
    return {"historical": True, "symbolic": True}


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
            # crawl4ai 0.9 may return object with raw_markdown
            if hasattr(m, "raw_markdown"):
                md = m.raw_markdown or ""
            elif isinstance(m, str):
                md = m
            else:
                md = str(m)
        html = getattr(result, "html", None) or ""
        # Cloudflare detection
        blob = (md + "\n" + html[:5000]).lower()
        if "cloudflare" in blob and ("attention required" in blob or "cf-browser-verification" in blob or "just a moment" in blob):
            return {"ok": False, "url": url, "error": "Cloudflare block", "status": status, "md": "", "html": html}
        if not ok:
            return {"ok": False, "url": url, "error": err or "crawl failed", "status": status, "md": md, "html": html}
        return {"ok": True, "url": url, "error": None, "status": status, "md": md, "html": html}
    except Exception as e:
        return {"ok": False, "url": url, "error": str(e), "status": None, "md": "", "html": ""}


async def fetch_archive_text_urls(crawler: AsyncWebCrawler, details_url: str) -> list[tuple[str, str]]:
    """Return list of (url, kind) for metadata page + preferred txt/html fulltext."""
    out: list[tuple[str, str]] = [(details_url, "metadata")]
    # Common IA plain text patterns for this item
    ident = "truefaithfulrela00deej"
    candidates = [
        f"https://archive.org/stream/{ident}/{ident}_djvu.txt",
        f"https://archive.org/download/{ident}/{ident}_djvu.txt",
        f"https://archive.org/stream/{ident}/{ident}_djvu.txt",
    ]
    # Also try metadata API (JSON) — allowlisted host
    meta_api = f"https://archive.org/metadata/{ident}"
    r = await crawl_url(crawler, meta_api)
    await asyncio.sleep(SLEEP_SEC)
    if r["ok"] and r["md"]:
        # try parse JSON from markdown/html
        raw = r.get("html") or r.get("md") or ""
        # if crawl got rendered text of JSON
        try:
            # find JSON object
            start = raw.find("{")
            end = raw.rfind("}")
            if start >= 0 and end > start:
                meta = json.loads(raw[start : end + 1])
                files = meta.get("files") or []
                # prefer .txt then .html
                txts = [f for f in files if str(f.get("name", "")).endswith(".txt")]
                htmls = [f for f in files if str(f.get("name", "")).endswith((".html", ".htm"))]
                for f in txts[:2]:
                    name = f["name"]
                    out.append((f"https://archive.org/download/{ident}/{name}", "fulltext_txt"))
                for f in htmls[:1]:
                    name = f["name"]
                    out.append((f"https://archive.org/download/{ident}/{name}", "fulltext_html"))
        except Exception:
            pass
    # Always try djvu.txt as fallback if nothing else
    if len(out) == 1:
        out.append((candidates[0], "fulltext_txt_guess"))
    return out


async def main() -> None:
    existing = load_existing_hashes()
    print(f"run_id={RUN_ID} existing_hashes={len(existing)}")

    browser_cfg = BrowserConfig(
        headless=True,
        verbose=False,
        user_agent=UA,
    )
    # BrowserConfig may take user_agent differently — set via headers if needed
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

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        for job in PLAN:
            seed = job["seed"]
            family = job["family_id"]
            license_ = job["license"]
            title_note = job.get("title_note")
            print(f"\n=== {family}: {seed} ===")

            queue: list[str] = []
            if job.get("archive_item"):
                pairs = await fetch_archive_text_urls(crawler, seed)
                # don't download huge binaries — only txt/html/metadata
                for u, kind in pairs:
                    if kind.startswith("fulltext") and not any(u.lower().endswith(ext) for ext in (".txt", ".html", ".htm")):
                        # skip if path looks like pdf/epub
                        if any(x in u.lower() for x in (".pdf", ".epub", ".djvu", ".zip", ".mp3", ".mobi")):
                            continue
                    queue.append(u)
                # Cap archive fulltext pages: metadata + at most 1 text file (may be long — we chunk)
                # Prefer first fulltext_txt
                meta = [u for u, k in pairs if k == "metadata"]
                texts = [u for u, k in pairs if "txt" in k]
                htmls = [u for u, k in pairs if "html" in k]
                queue = meta[:1] + texts[:1] + (htmls[:1] if not texts else [])
            else:
                queue = [seed]

            crawled_for_job: set[str] = set()
            children_added = 0
            max_children = job.get("max_children") or 0

            while queue:
                url = queue.pop(0)
                url = normalize_url(url)
                if url in crawled_for_job:
                    continue
                if not host_ok(url):
                    failures.append({"url": url, "error": "host not allowlisted"})
                    continue
                # skip huge binary extensions
                path_l = urlparse(url).path.lower()
                if any(path_l.endswith(ext) for ext in (".pdf", ".epub", ".zip", ".djvu", ".mp3", ".mobi", ".gz")):
                    failures.append({"url": url, "error": "skipped binary extension"})
                    continue

                print(f"  crawl {url}")
                result = await crawl_url(crawler, url)
                crawled_for_job.add(url)
                urls_attempted.append({"url": url, "family_id": family, "ok": result["ok"], "status": result.get("status"), "error": result.get("error")})
                await asyncio.sleep(SLEEP_SEC)

                if not result["ok"]:
                    failures.append({"url": url, "error": result.get("error"), "status": result.get("status")})
                    print(f"    FAILED: {result.get('error')}")
                    continue

                pages_ok += 1
                md = clean_markdown(result["md"] or "")
                # For archive metadata JSON pages, extract readable description
                if "archive.org/metadata/" in url or ("archive.org/details/" in url and len(md) < 500):
                    # keep whatever we have; also try plain text from html strip
                    if not md and result.get("html"):
                        md = clean_markdown(re.sub(r"<[^>]+>", " ", result["html"]))

                # Discover children from seed (or first page)
                if max_children > 0 and children_added < max_children and url == seed:
                    src = (result.get("html") or "") + "\n" + (result.get("md") or "")
                    kids = extract_same_host_links(
                        src, seed, job.get("path_prefix"), job.get("child_glob")
                    )
                    for k in kids:
                        if children_added >= max_children:
                            break
                        if k not in crawled_for_job and k not in queue:
                            queue.append(k)
                            children_added += 1
                    print(f"    queued {children_added} children")

                if len(md) < MIN_PAGE_CHARS:
                    print(f"    skip empty/nav-only ({len(md)} chars)")
                    continue

                # Cap extremely long archive txt to first ~120k chars to avoid memory blow
                if len(md) > 120_000:
                    md = md[:120_000]
                    print("    truncated long text to 120k chars")

                chunks = chunk_paragraphs(md)
                print(f"    text={len(md)} chars -> {len(chunks)} chunks")

                for i, chunk in enumerate(chunks):
                    ch = content_hash(chunk)
                    if ch in existing:
                        atoms_skipped_dupe += 1
                        continue
                    aid = atom_id_for(family, ch)
                    atom = {
                        "atom_id": aid,
                        "family_id": family,
                        "type": "text",
                        "text": chunk,
                        "license": license_,
                        "source_url": url,
                        "epistemic": "INFERRED",
                        "content_hash": ch,
                        "lens_hints": lens_for(family, title_note),
                    }
                    with ATOMS_PATH.open("a") as f:
                        f.write(json.dumps(atom, ensure_ascii=False) + "\n")
                    existing.add(ch)
                    atoms_written += 1
                    by_family[family] = by_family.get(family, 0) + 1
                    if len(sample_ids) < 3:
                        sample_ids.append(aid)

    receipt = {
        "run_id": RUN_ID,
        "engine": "crawl4ai",
        "engine_version": "0.9.3",
        "started_note": "Wave 0 Enochian-first harvest",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "atom_count": atoms_written,
        "atoms_skipped_dupe": atoms_skipped_dupe,
        "pages_ok": pages_ok,
        "urls": urls_attempted,
        "failures": failures,
        "by_family": by_family,
        "atoms_path": str(ATOMS_PATH),
        "user_agent": UA,
        "epistemic_policy": "INFERRED for crawl (do not claim OBSERVED on atoms)",
    }
    receipt_path = RECEIPTS_DIR / f"{RUN_ID}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False))

    # Scoreboard
    lines = [
        "# Wave 0 Enochian harvest scoreboard",
        "",
        f"- run_id: `{RUN_ID}`",
        "- engine: crawl4ai 0.9.3",
        f"- timestamp_utc: {receipt['timestamp_utc']}",
        f"- atoms_written: **{atoms_written}**",
        f"- atoms_skipped_dupe: {atoms_skipped_dupe}",
        f"- pages_ok: {pages_ok}",
        f"- failures: {len(failures)}",
        f"- receipt: `{receipt_path}`",
        f"- atoms: `{ATOMS_PATH}`",
        "",
        "## Counts by family_id",
        "",
    ]
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
    lines.append("- goetia_catalog stored as historical text; lens operational=false.")
    lines.append("- Corpus written under ~/.athanor/ — not committed to git.")
    scoreboard_path = SCOREBOARD_DIR / f"wave0-enochian-{TS_LOCAL}.md"
    scoreboard_path.write_text("\n".join(lines) + "\n")

    print("\n==== DONE ====")
    print(json.dumps({"atoms_written": atoms_written, "by_family": by_family, "receipt": str(receipt_path), "scoreboard": str(scoreboard_path), "failures": len(failures), "sample_ids": sample_ids}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
