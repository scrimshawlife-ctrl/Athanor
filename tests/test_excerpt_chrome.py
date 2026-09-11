"""Retrieve-time chrome strip — sacred-texts SPA nav must not own excerpts."""

from __future__ import annotations

from athanor.chrome import strip_chrome
from athanor.retrieve import Atom, build_packet

# Flattened crawl4ai-style atom: SPA chrome, then tradition body.
# Mirrors live SoT excerpts that start at breadcrumb "[Categories](...) [Enochian Magic]".
_SPA_CHROME_PREFIX = """
[View the original site…](https://archive.sacred-texts.com/)
Hide
Close navigation
[![Internet Sacred Text Archive](/og-logo.png)](https://sacred-texts.com/)
* + [African](https://sacred-texts.com/categories/african)
  + [Freemasonry](https://sacred-texts.com/categories/freemasonry)
  + [Alchemy](https://sacred-texts.com/categories/alchemy)
Toggle Sidebar
[Sign in](https://sacred-texts.com/login) [Sign up](https://sacred-texts.com/subscribe)
[Buy USB Drive](https://sacred-texts.com/shop/usb) The archive, offline Own the Wisdom of the Ages. Every text in the library on a single USB drive.
[Home](https://sacred-texts.com/) [Categories](https://sacred-texts.com/categories "Categories") [Enochian Magic](https://sacred-texts.com/categories/enochian-magic "Enochian Magic") [The Calls of Enoch](https://sacred-texts.com/eso/enoch/callench.htm "The Calls of Enoch")
"""

_CALLS_BODY = (
    "# THE FIRST KEY\n\n"
    "I reign over you, saith the God of Justice, in power exalted above "
    "the firmament of wrath. These Calls form the liturgical Keys recorded "
    "from Dee and Kelley scrying sessions.\n"
)


def _polluted_atom() -> Atom:
    return Atom.from_mapping(
        {
            "atom_id": "fixture.enochian.calls.chrome",
            "family_id": "enochian",
            "text": _SPA_CHROME_PREFIX + _CALLS_BODY,
            "license": "CC0-fixture",
            "epistemic": "INFERRED",
        }
    )


def test_strip_chrome_drops_nav_keeps_calls_body():
    cleaned = strip_chrome(_SPA_CHROME_PREFIX + _CALLS_BODY)
    lower = cleaned.lower()
    assert "categories" not in lower
    assert "toggle sidebar" not in lower
    assert "sign in" not in lower
    assert "buy usb" not in lower
    assert "sacred-texts.com/categories" not in lower
    assert "FIRST KEY" in cleaned
    assert "reign over you" in cleaned.lower()
    assert "Calls" in cleaned


def test_excerpt_skips_breadcrumb_chrome_for_enochian_query():
    packet = build_packet("Enochian Calls", [(_polluted_atom(), 1.0)])
    excerpt = packet["hits"][0]["excerpt"]
    assert packet["efficacy"] is None
    assert "Categories" not in excerpt
    assert "sacred-texts.com/categories" not in excerpt
    assert "Toggle Sidebar" not in excerpt
    assert "FIRST KEY" in excerpt or "reign over you" in excerpt.lower()


def test_excerpt_windows_around_query_in_cleaned_body():
    # Query token "Calls" also occurs in breadcrumb chrome; strip first or
    # the 280-char window stays stuck on the nav chain.
    filler = "Historical note on the tablet arrangement. " * 20
    text = _SPA_CHROME_PREFIX + filler + _CALLS_BODY
    atom = Atom.from_mapping(
        {
            "atom_id": "fixture.enochian.calls.chrome.long",
            "family_id": "enochian",
            "text": text,
            "license": "CC0-fixture",
            "epistemic": "INFERRED",
        }
    )
    packet = build_packet("Calls", [(atom, 1.0)])
    excerpt = packet["hits"][0]["excerpt"]
    assert "Calls form the liturgical Keys" in excerpt
    assert "Categories" not in excerpt
    assert "Enochian Magic](" not in excerpt


def test_strip_chrome_is_noop_on_clean_prose():
    prose = (
        "The First Enochian Call opens the angelical Keys recorded in "
        "Dee and Kelley scrying sessions."
    )
    assert strip_chrome(prose) == prose


def test_strip_chrome_keeps_in_body_tradition_words():
    # Category labels are chrome only as nav lists, not as essay words.
    prose = (
        "Secondary notes compare Freemasonry reception of Enochian material "
        "with African diaspora catalog essays."
    )
    cleaned = strip_chrome(prose)
    assert "Freemasonry" in cleaned
    assert "African" in cleaned


def test_in_body_markdown_link_unwraps_to_label():
    prose = (
        "Consult [The Calls of Enoch](https://sacred-texts.com/eso/enoch/callench.htm) "
        "for the Keys."
    )
    cleaned = strip_chrome(prose)
    assert "Calls of Enoch" in cleaned
    assert "for the Keys" in cleaned
    assert "sacred-texts.com" not in cleaned
    assert "callench.htm)" not in cleaned


def test_ritual_english_is_not_eaten_by_chrome_phrases():
    prose = (
        "Make the Sign in the East, then the Sign in the West. "
        "The angels assign in due order the parts of the tablet. "
        "They sign up the names upon the Holy Table. "
        "Each become a member of the chorus of angels."
    )
    cleaned = strip_chrome(prose)
    assert "Sign in the East" in cleaned
    assert "assign in due order" in cleaned
    assert "sign up the names" in cleaned
    assert "become a member of the chorus" in cleaned


def test_adjacent_content_citations_are_kept_as_labels():
    prose = (
        "See [Liber Loagaeth](https://example.invalid/loagaeth) "
        "[Liber Mysteriorum](https://example.invalid/mysteriorum) "
        "and note [1](#fn1)."
    )
    cleaned = strip_chrome(prose)
    assert "Liber Loagaeth" in cleaned
    assert "Liber Mysteriorum" in cleaned
    assert "1" in cleaned
    assert "example.invalid" not in cleaned


def test_linked_heading_after_nav_is_kept():
    prose = (
        "[Home](https://sacred-texts.com/)\n\n"
        "[THE FIRST KEY](https://sacred-texts.com/eso/enoch/callench.htm)\n\n"
        "I reign over you."
    )
    cleaned = strip_chrome(prose)
    assert "FIRST KEY" in cleaned
    assert "reign over you" in cleaned.lower()


def test_archive_content_citation_keeps_title():
    prose = (
        "Consult [The Calls of Enoch]"
        "(https://archive.sacred-texts.com/eso/enoch/callench.htm) "
        "for the Keys."
    )
    cleaned = strip_chrome(prose)
    assert "Calls of Enoch" in cleaned
    assert "for the Keys" in cleaned


def test_chrome_only_atom_yields_empty_excerpt():
    atom = Atom.from_mapping(
        {
            "atom_id": "fixture.chrome.only",
            "family_id": "enochian",
            "text": _SPA_CHROME_PREFIX,
            "license": "CC0-fixture",
            "epistemic": "INFERRED",
        }
    )
    packet = build_packet("Enochian", [(atom, 1.0)])
    assert packet["hits"][0]["excerpt"] == ""
    assert packet["efficacy"] is None
