"""
QuantEarningsPro — Glossary Service (JSON-backed, Cloud Run compatible)
=========================================================================
Loads glossary.json from the static directory once at startup.
No database required — works on Cloud Run's ephemeral filesystem.
"""

import json
import os
import re
import logging
from typing import Optional

log = logging.getLogger(__name__)

# Path to the JSON file bundled in the container image
_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "app", "static", "glossary.json")
_FALLBACK_PATH = "app/static/glossary.json"

# In-memory cache — populated once at startup
_TERMS: list[dict] = []
_BY_SLUG: dict[str, dict] = {}


def _normalize(raw: dict) -> dict:
    """Map glossary.json field names to the field names the template expects."""
    qep = raw.get("qep_link", {})
    if isinstance(qep, str):
        qep = {}
    return {
        "slug":        raw.get("id", ""),
        "term":        raw.get("term", ""),
        "category":    raw.get("category", "General"),
        "definition":  raw.get("definition", ""),
        "explanation": raw.get("explanation", ""),
        "qep_url":     qep.get("url", ""),
        "qep_anchor":  qep.get("anchor_text", ""),
        "wiki_url":    raw.get("wikipedia_url", ""),
    }


def _load() -> None:
    """Load and cache glossary.json. Called once at import time."""
    global _TERMS, _BY_SLUG
    for path in (_JSON_PATH, _FALLBACK_PATH, "glossary.json"):
        try:
            with open(path, encoding="utf-8") as f:
                raw = json.load(f)
            items = raw if isinstance(raw, list) else raw.get("terms", [])
            _TERMS = [_normalize(t) for t in items]
            _BY_SLUG = {t["slug"]: t for t in _TERMS}
            log.info(f"Glossary loaded: {len(_TERMS)} terms from {path}")
            return
        except FileNotFoundError:
            continue
        except Exception as e:
            log.error(f"Failed to load glossary from {path}: {e}")
    log.warning("glossary.json not found — glossary will be empty")


_load()


# Public API

def get_all_terms() -> list[dict]:
    """Return all terms, sorted by category then term name."""
    return sorted(_TERMS, key=lambda t: (t["category"], t["term"]))


def get_by_slug(slug: str) -> Optional[dict]:
    """Return a single term by its slug, or None."""
    return _BY_SLUG.get(slug)


def search_terms(query: str) -> list[dict]:
    """
    Simple case-insensitive substring search across term name and definition.
    Returns matching terms sorted by relevance (exact match first).
    """
    q = query.strip().lower()
    if not q or len(q) < 2:
        return get_all_terms()

    exact, partial = [], []
    for t in _TERMS:
        term_lower = t["term"].lower()
        if term_lower == q or t["slug"] == q:
            exact.append(t)
        elif q in term_lower or q in t["definition"].lower():
            partial.append(t)

    return exact + sorted(partial, key=lambda t: t["term"])


def group_by_category(terms: list[dict]) -> dict[str, list[dict]]:
    """Group a list of terms into an ordered dict keyed by category."""
    category_order = [
        "Earnings & Fundamentals",
        "Options & Volatility",
        "Technical Indicators",
        "Market & Macro",
        "Quantitative Metrics",
        "Market Structure",
        "Commodities & Futures",
        "Industry Terms",
        "General",
    ]
    grouped: dict[str, list[dict]] = {}
    for t in terms:
        cat = t.get("category", "General")
        grouped.setdefault(cat, []).append(t)

    ordered: dict[str, list[dict]] = {}
    for cat in category_order:
        if cat in grouped:
            ordered[cat] = grouped[cat]
    for cat in sorted(grouped.keys()):
        if cat not in ordered:
            ordered[cat] = grouped[cat]
    return ordered
