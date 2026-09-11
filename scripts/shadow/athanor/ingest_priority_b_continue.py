#!/usr/bin/env python3
"""Priority B continue — rebalance underfilled correspondence kinds."""
from __future__ import annotations
import asyncio
import ingest_priority_b as b

M = b.MIRROR_HOST

# Gap-fill plan: prefer underrepresented kinds; soft_caps are SESSION totals (incl. prior PB)
b.PLAN = [
    {
        "family_id": "iching_daoist",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "correspondence",
        "correspondence_kind": "hexagram-judgment",
        "urls": [f"{M}/ich/ic{n:02d}.htm" for n in list(range(7, 33)) + list(range(33, 57))],
        "soft_cap": 22,
        "one_atom_per_page": True,
        "prefer_tables": False,
        "keywords": ["hexagram", "judgment", "nine", "six", "trigram"],
    },
    {
        "family_id": "kabbalah_pd",
        "license": "public-domain",
        "reception_layer": "historical_commentary",
        "type": "correspondence",
        "correspondence_kind": "sephirah-path",
        "urls": [
            f"{M}/jud/cab/cab07.htm",
            f"{M}/jud/cab/cab04.htm",
            f"{M}/jud/tku/tku07.htm",
            f"{M}/jud/tku/tku08.htm",
            f"{M}/jud/jm/jm09.htm",
            f"{M}/jud/jm/jm10.htm",
            f"{M}/jud/jm/jm11.htm",
        ],
        "soft_cap": 26,
        "prefer_tables": True,
        "keywords": [
            "sephir", "sephiroth", "path", "emanation", "kether", "chokmah",
            "binah", "chesed", "geburah", "tiphareth", "netzach", "hod",
            "yesod", "malkuth", "tree",
        ],
    },
    {
        "family_id": "hermetic",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "table",
        "correspondence_kind": "planet-metal",
        "urls": [
            f"{M}/grim/magus/ma132.htm",
            f"{M}/grim/magus/ma141.htm",
            f"{M}/grim/magus/ma144.htm",
            f"{M}/grim/magus/ma147.htm",
            f"{M}/grim/magus/ma148.htm",
            f"{M}/grim/magus/ma149.htm",
            f"{M}/grim/magus/ma150.htm",
            f"{M}/grim/magus/ma138.htm",
            f"{M}/grim/magus/ma140.htm",
        ],
        "soft_cap": 22,
        "prefer_tables": True,
        "force_type_if_table": "table",
        "keywords": [
            "planet", "metal", "gold", "silver", "iron", "copper", "tin",
            "lead", "mercury", "scale", "element", "saturn", "jupiter",
            "mars", "venus", "sun", "moon", "table",
        ],
    },
    {
        "family_id": "hermetic",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "correspondence",
        "correspondence_kind": "element-direction",
        "urls": [
            f"{M}/grim/magus/ma127.htm",
            f"{M}/grim/magus/ma128.htm",
            f"{M}/grim/magus/ma129.htm",
            f"{M}/grim/magus/ma130.htm",
            f"{M}/grim/magus/ma131.htm",
            f"{M}/grim/magus/ma126.htm",
        ],
        "soft_cap": 22,
        "prefer_tables": True,
        "keywords": [
            "element", "fire", "water", "air", "earth", "east", "west",
            "north", "south", "quarter", "direction", "wind",
        ],
    },
    {
        "family_id": "astrology_west",
        "license": "public-domain",
        "reception_layer": "period_translation",
        "type": "correspondence",
        "correspondence_kind": "planet-day-hour",
        "urls": [
            f"{M}/astro/ptb/ptb06.htm",
            f"{M}/astro/ptb/ptb07.htm",
            f"{M}/astro/ptb/ptb08.htm",
            f"{M}/astro/ptb/ptb31.htm",
            f"{M}/grim/magus/ma155.htm",
            f"{M}/grim/kos/kos07.htm",
        ],
        "soft_cap": 18,
        "prefer_tables": True,
        "keywords": [
            "hour", "hours", "day", "planet", "saturn", "jupiter", "mars",
            "sun", "venus", "mercury", "moon", "mansion", "influence",
        ],
    },
]

# Fairer balance for continue: only enforce after more mass; allow catch-up
_orig_balance = b.balance_allows

def balance_allows(by_family_new, family):
    total_new = sum(by_family_new.values())
    if total_new <= 0:
        return True
    projected = by_family_new.get(family, 0) + 1
    # Soft phase until 80 NEW across Priority B session
    if total_new + 1 < 80:
        return True
    return (projected / (total_new + 1)) <= (b.BALANCE_FRAC + 0.001)

b.balance_allows = balance_allows
b.TARGET_MAX = 46  # remaining to ~120 session total
b.TARGET_MIN = 40
# Refresh run ids
from datetime import datetime, timezone
import uuid
b.RUN_TS = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
b.RUN_ID = f"ingest-priority-b-{b.RUN_TS}-{uuid.uuid4().hex[:8]}"
b.TS_FILE = b.RUN_TS
# HOLD already includes static; note continue
b.HOLD_STATIC = list(b.HOLD_STATIC) + [{"reason": "continue-pass rebalance for underfilled kinds (hexagram/sephirah/magus scales)"}]

print("continue run_id", b.RUN_ID)
asyncio.run(b.main())
