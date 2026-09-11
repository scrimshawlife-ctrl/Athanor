"""Retrieve-time nav/chrome strip for harvested markdown (sacred-texts SPA and similar).

Does not rewrite stored corpus atoms. Stdlib only. Safe on clean prose.
"""

from __future__ import annotations

import re
from itertools import pairwise
from urllib.parse import urlparse

# Nested logo: [![alt](src)](href)
_NESTED_IMAGE_LINK = re.compile(r"\[!\[[^\]]*\]\([^)]+\)\]\([^)]+\)")
_MD_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]+\)")
_MD_LINK = re.compile(r"\[(?P<text>[^\]]*)\]\((?P<dest>[^)]+)\)")
_LINK_GAP = re.compile(r"^[\s*+\-|•]+$")
_ORPHAN_MARKDOWN = re.compile(r"\]\([^)]*\)|\[[^\]]*\]\(")
_ORPHAN_LIST = re.compile(r"(?m)^[\s*+\-|•]+$")
_STANDALONE_HIDE = re.compile(r"(?im)^hide\s*$")

_CHROME_PATH_MARKERS = (
    "/categories",
    "/shop",
    "/login",
    "/subscribe",
    "/search",
    "/rankings",
    "/support",
    "/new.htm",
    "/about",
    "/abuse",
    "/contact",
    "/donate",
    "/faq.htm",
    "/privacy",
    "/terms",
    "/dmca",
    "/og-logo",
    "/img?",
)

_CHROME_LABELS = frozenset(
    {
        "home",
        "categories",
        "search",
        "rankings",
        "shop",
        "sign in",
        "sign up",
        "buy usb drive",
        "hide",
        "close navigation",
        "toggle sidebar",
        "internet sacred text archive",
        "back to book",
        "clear cache",
        "feedback",
        "support",
    }
)

_CHROME_PHRASES = (
    "to view the original internet sacred text archive",
    "view the original site",
    "visit archive.sacred-texts.com",
    "sign in access your account",
    "close navigation",
    "toggle sidebar",
    "the archive, offline",
    "own the wisdom of the ages",
    "every text in the library on a single usb drive",
    "read offline, cite freely, keep forever",
    "no subscription required",
    "get the drive",
    "buy usb drive",
    "support the archive",
    "read ad-free",
    "become a member",
    "comments and social are coming soon",
    "reader conversations and shared activity will appear here",
    "sign in",
    "sign up",
)

_PHRASE_RE = re.compile(
    "|".join(re.escape(p) for p in sorted(_CHROME_PHRASES, key=len, reverse=True)),
    re.IGNORECASE,
)


def strip_chrome(text: str) -> str:
    """Remove site nav/chrome from harvested markdown.

    Retrieve-time only: does not rewrite stored corpus atoms. Unchanged when
    the input has no chrome patterns.
    """
    if not text:
        return ""

    cleaned = _NESTED_IMAGE_LINK.sub(" ", text)
    cleaned = _MD_IMAGE.sub(" ", cleaned)
    cleaned = _drop_link_runs(cleaned)
    cleaned = _drop_chrome_links(cleaned)
    cleaned = _PHRASE_RE.sub(" ", cleaned)
    cleaned = _STANDALONE_HIDE.sub("", cleaned)
    cleaned = _ORPHAN_MARKDOWN.sub(" ", cleaned)
    cleaned = _ORPHAN_LIST.sub("", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = cleaned.strip()
    if not re.search(r"[A-Za-z0-9]", cleaned):
        return ""
    return cleaned


def _href_from_dest(dest: str) -> str:
    token = dest.strip()
    if token.startswith("<") and ">" in token:
        token = token[1 : token.index(">")].strip()
    parts = token.split(None, 1)
    return parts[0] if parts else token


def _href_is_chrome(href: str) -> bool:
    token = href.strip()
    if not token or token.startswith(("#", "javascript:")):
        return True
    lowered = token.lower()
    if "archive.sacred-texts.com" in lowered:
        return True
    parsed = urlparse(token if "://" in token else f"https://chrome.invalid/{token}")
    host = (parsed.hostname or "").lower()
    path = (parsed.path or "").lower()
    if host.endswith("sacred-texts.com") and path in ("", "/"):
        return True
    compact = path.replace(".", "").replace("/", "")
    if compact == "":
        return True
    blob = f"{lowered} {path}"
    return any(marker in blob for marker in _CHROME_PATH_MARKERS)


def _label_is_chrome(label: str) -> bool:
    s = re.sub(r"[\s.…]+$", "", label.strip().lower())
    s = re.sub(r"\s+", " ", s)
    if s in _CHROME_LABELS:
        return True
    return s.startswith("view the original") or "usb drive" in s


def _drop_spans(text: str, spans: list[tuple[int, int]]) -> str:
    if not spans:
        return text
    parts: list[str] = []
    cursor = 0
    for start, end in sorted(spans):
        if start < cursor:
            continue
        parts.append(text[cursor:start])
        parts.append(" ")
        cursor = end
    parts.append(text[cursor:])
    return "".join(parts)


def _drop_link_runs(text: str) -> str:
    matches = list(_MD_LINK.finditer(text))
    if not matches:
        return text
    drop: list[tuple[int, int]] = []
    run_start = matches[0].start()
    run_end = matches[0].end()
    run_len = 1
    for prev, cur in pairwise(matches):
        gap = text[prev.end() : cur.start()]
        if _LINK_GAP.match(gap):
            run_end = cur.end()
            run_len += 1
            continue
        if run_len >= 2:
            drop.append((run_start, run_end))
        run_start = cur.start()
        run_end = cur.end()
        run_len = 1
    if run_len >= 2:
        drop.append((run_start, run_end))
    return _drop_spans(text, drop)


def _drop_chrome_links(text: str) -> str:
    drop: list[tuple[int, int]] = []
    for match in _MD_LINK.finditer(text):
        href = _href_from_dest(match.group("dest"))
        label = match.group("text")
        if _href_is_chrome(href) or _label_is_chrome(label):
            drop.append(match.span())
    return _drop_spans(text, drop)
