"""Athanor — tradition corpus + encoder (SHADOW)."""

from pathlib import Path

__version__ = (Path(__file__).resolve().parents[2] / "VERSION").read_text(encoding="utf-8").strip()

__all__ = ["__version__", "retrieve"]


def __getattr__(name: str):
    if name == "retrieve":
        from athanor.retrieve import retrieve as _retrieve

        return _retrieve
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
