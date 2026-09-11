"""Retrieve-time nav/chrome strip for harvested markdown (sacred-texts SPA and similar).

Does not rewrite stored corpus atoms. Stdlib only. Remaining markdown links unwrap
to their labels so excerpts stay readable.
"""

from __future__ import annotations

import re
from itertools import pairwise
from urllib.parse import urlparse

_NESTED_IMAGE_LINK = re.compile(r"\[!\[[^\]]*\]\([^)]+\)\]\([^)]+\)")
_MD_IMAGE = re.compile(r"!\[(?P<alt>[^\]]*)\]\([^)]+\)")
_MD_LINK = re.compile(r"\[(?P<text>[^\]]*)\]\((?P<dest>[^)]+)\)")
_LINK_GAP = re.compile(r"^[\s*+\-|•]+$")
_ORPHAN_CLOSE = re.compile(r"\]\([^)]*\)")
_ORPHAN_LIST = re.compile(r"(?m)^[\s*+\-|•]+$")

_CHROME_PATH_MARKERS = (
    "/categories",
    "/shop",
    "/login",
    "/subscribe",
    "/search",
    "/rankings",
    "/support",
    "/new.htm",
    "/about.htm",
    "/abuse.htm",
    "/contact.htm",
    "/donate.htm",
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

_STANDALONE_CHROME_LINE = re.compile(
    r"(?im)^(?:"
    r"hide|sign in|sign up|toggle sidebar|close navigation|"
    r"view the original site|buy usb drive|clear cache|"
    r"back to book"
    r")[.…]*\s*$"
)

# Distinctive SPA/shop copy only — not short English ("sign in", "become a member").
_CHROME_PHRASES = (
    "to view the original internet sacred text archive",
    "visit archive.sacred-texts.com",
    "sign in access your account",
    "close navigation",
    "toggle sidebar",
    "the archive, offline",
    "own the wisdom of the ages",
    "every text in the library on a single usb drive",
    "read offline, cite freely, keep forever",
    "comments and social are coming soon",
    "reader conversations and shared activity will appear here",
)

_PHRASE_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:"
    + "|".join(re.escape(p) for p in sorted(_CHROME_PHRASES, key=len, reverse=True))
    + r")(?![A-Za-z0-9])",
    re.IGNORECASE,
)


def strip_chrome(text: str) -> str:
    """Remove site nav/chrome from harvested markdown.

    Retrieve-time only: does not rewrite stored corpus atoms. Clean prose and
    in-body citations are kept (markdown links unwrap to labels).
    """
    if not text:
        return ""

    cleaned = _NESTED_IMAGE_LINK.sub(" ", text)
    cleaned = _MD_IMAGE.sub(_image_to_alt, cleaned)
    cleaned = _drop_chrome_link_runs(cleaned)
    cleaned = _drop_chrome_links(cleaned)
    cleaned = _MD_LINK.sub(_unwrap_link, cleaned)
    cleaned = _PHRASE_RE.sub(" ", cleaned)
    cleaned = _STANDALONE_CHROME_LINE.sub("", cleaned)
    cleaned = _ORPHAN_CLOSE.sub(" ", cleaned)
    cleaned = _ORPHAN_LIST.sub("", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = cleaned.strip()
    if not re.search(r"[A-Za-z0-9]", cleaned):
        return ""
    return cleaned


def _image_to_alt(match: re.Match[str]) -> str:
    alt = match.group("alt").strip()
    if not alt or _label_is_chrome(alt):
        return " "
    return alt


def _unwrap_link(match: re.Match[str]) -> str:
    return match.group("text") or " "


def _href_from_dest(dest: str) -> str:
    token = dest.strip()
    if token.startswith("<") and ">" in token:
        token = token[1 : token.index(">")].strip()
    parts = token.split(None, 1)
    return parts[0] if parts else token


def _parse_href(href: str) -> tuple[str, str, str]:
    token = href.strip()
    lowered = token.lower()
    if "://" in token:
        parsed = urlparse(token)
        host = (parsed.hostname or "").lower()
        path = (parsed.path or "").lower()
        return lowered, host, path
    path = lowered.split("?")[0].split("#")[0]
    return lowered, "", path


def _href_is_chrome(href: str) -> bool:
    token = href.strip()
    if not token or token.startswith("javascript:"):
        return True
    if token.startswith("#"):
        return token == "#"
    lowered, host, path = _parse_href(token)
    if host == "archive.sacred-texts.com" and path in ("", "/"):
        return True
    if host.endswith("sacred-texts.com") and path in ("", "/"):
        return True
    if host == "" and path.replace(".", "").replace("/", "") == "":
        return True
    blob = f"{lowered} {path}"
    return any(marker in blob for marker in _CHROME_PATH_MARKERS)


def _label_is_chrome(label: str) -> bool:
    s = re.sub(r"[\s.…]+$", "", label.strip().lower())
    s = re.sub(r"\s+", " ", s)
    if s in _CHROME_LABELS:
        return True
    return s.startswith("view the original") or "usb drive" in s


def _link_is_chrome(match: re.Match[str]) -> bool:
    href = _href_from_dest(match.group("dest"))
    return _href_is_chrome(href) or _label_is_chrome(match.group("text"))


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


def _drop_chrome_link_runs(text: str) -> str:
    matches = list(_MD_LINK.finditer(text))
    if not matches:
        return text
    drop: list[tuple[int, int]] = []
    run = [matches[0]]
    for prev, cur in pairwise(matches):
        gap = text[prev.end() : cur.start()]
        if _LINK_GAP.match(gap):
            run.append(cur)
            continue
        _flush_chrome_run(run, drop)
        run = [cur]
    _flush_chrome_run(run, drop)
    return _drop_spans(text, drop)


def _flush_chrome_run(
    run: list[re.Match[str]],
    drop: list[tuple[int, int]],
) -> None:
    if len(run) >= 2 and any(_link_is_chrome(m) for m in run):
        drop.append((run[0].start(), run[-1].end()))


def _drop_chrome_links(text: str) -> str:
    drop = [m.span() for m in _MD_LINK.finditer(text) if _link_is_chrome(m)]
    return _drop_spans(text, drop)
