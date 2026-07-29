"""Loads the generated 50-unit curriculum (curriculum_data.json) into the data
structures the app expects: UNITS (English source), UNIT_T / LESSON_T (de/es
translations), plus LESSON_MAP / LESSON_ORDER. Re-exports BADGES, STOCK_T etc.

If a unit is missing from the JSON (e.g. generation still running) it is simply
skipped, so the app always boots with whatever content is ready.
"""
import json
from pathlib import Path

from curriculum_blueprint import UNITS_SPEC, TIER_META
from content import BADGES, BADGE_MAP
from content_i18n import STOCK_T, norm_lang

_DATA_PATH = Path(__file__).parent / "curriculum_data.json"
_DATA = json.loads(_DATA_PATH.read_text(encoding="utf-8")) if _DATA_PATH.exists() else {}

UNITS = []
UNIT_T = {"de": {}, "es": {}}
LESSON_T = {"de": {}, "es": {}}

for _spec in UNITS_SPEC:
    _uid = _spec["id"]
    _d = _DATA.get(_uid)
    if not _d:
        continue
    _lessons_en = []
    for _lspec, _lgen in zip(_spec["lessons"], _d["lessons"]):
        _en = _lgen["en"]
        _lessons_en.append({
            "id": _lspec["id"],
            "title": _lspec["title"],
            "icon": _lspec["icon"],
            "xp": _spec["xp"],
            "cards": _en["cards"],
            "questions": [
                {"q": q["q"], "options": q["options"], "answer": q["answer"], "explain": q["explain"]}
                for q in _en["questions"]
            ],
        })
        for _lg in ("de", "es"):
            _g = _lgen[_lg]
            LESSON_T[_lg][_lspec["id"]] = {
                "title": _g["title"],
                "cards": _g["cards"],
                "questions": [
                    {"q": q["q"], "options": q["options"], "explain": q["explain"]}
                    for q in _g["questions"]
                ],
            }
    UNITS.append({
        "id": _uid,
        "title": _spec["title"],
        "subtitle": _spec["subtitle"],
        "color": _spec["color"],
        "tier": _spec["tier"],
        "lessons": _lessons_en,
    })
    for _lg in ("de", "es"):
        UNIT_T[_lg][_uid] = {
            "title": _d["unit"][_lg]["title"],
            "subtitle": _d["unit"][_lg]["subtitle"],
        }

# Flatten lessons for quick lookup
LESSON_MAP = {}
LESSON_ORDER = []
for _u in UNITS:
    for _l in _u["lessons"]:
        LESSON_MAP[_l["id"]] = {
            **_l, "unit_id": _u["id"], "unit_title": _u["title"],
            "unit_color": _u["color"], "tier": _u["tier"],
        }
        LESSON_ORDER.append(_l["id"])

# Lessons grouped by difficulty tier (for endless Practice mode)
LESSONS_BY_TIER = {t: [] for t in TIER_META}
for _lid, _l in LESSON_MAP.items():
    LESSONS_BY_TIER[_l["tier"]].append(_lid)

__all__ = [
    "UNITS", "UNIT_T", "LESSON_T", "LESSON_MAP", "LESSON_ORDER",
    "LESSONS_BY_TIER", "BADGES", "BADGE_MAP", "STOCK_T", "norm_lang", "TIER_META",
]
