"""
normtrace.standards
===================
Standards loader: exposes CRPD articles and General Comments as structured
Python objects loaded from ``data/crpd/``.

This module is the interface through which the rest of the package (and the
LLM extraction layer) accesses the normative standard. Callers should never
parse the JSON files directly; they should use the functions here.

All functions are pure (no side effects beyond the initial file load) and
return immutable objects (frozen dataclasses).
"""

from __future__ import annotations

import json
from pathlib import Path

from normtrace.models import (
    BindingForce,
    CRPDArticle,
    CRPDPrinciple,
    GeneralComment,
    GapSeverity,
    GapType,
    MinimumStandard,
    ObligationType,
    RedFlag,
)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

_CRPD_PATH = Path(__file__).parent.parent / "data" / "crpd"


def _load_articles() -> dict[int, CRPDArticle]:
    """Load all CRPD articles from ``data/crpd/articles.json``."""
    with open(_CRPD_PATH / "articles.json", encoding="utf-8") as f:
        raw = json.load(f)

    articles: dict[int, CRPDArticle] = {}

    def _parse_article(entry: dict) -> CRPDArticle:
        return CRPDArticle(
            number=entry["number"],
            title=entry["title"],
            obligation_types=[ObligationType(o) for o in entry.get("obligation_types", [])],
            minimum_standards=[
                MinimumStandard(
                    description=ms["description"],
                    source_article=ms["source_article"],
                    source_paragraphs=ms.get("source_paragraphs", []),
                    general_comment_ids=ms.get("general_comment_ids", []),
                )
                for ms in entry.get("minimum_standards", [])
            ],
            red_flags=[
                RedFlag(
                    pattern=rf["pattern"],
                    gap_type=GapType(rf["gap_type"]),
                    severity_presumption=GapSeverity(rf["severity_presumption"]),
                    relevant_article=rf["relevant_article"],
                    rationale=rf.get("rationale", ""),
                )
                for rf in entry.get("red_flags", [])
            ],
            interpretive_authority=entry.get("interpretive_authority", []),
            cross_cutting=entry.get("cross_cutting", False),
            notes=entry.get("notes", ""),
        )

    # General principles (Art. 3) — stored separately
    gp = raw.get("general_principles")
    if gp:
        art3 = CRPDArticle(
            number=3,
            title=gp["title"],
            obligation_types=[ObligationType(o) for o in gp.get("obligation_types", [])],
            minimum_standards=[],
            red_flags=[
                RedFlag(
                    pattern=rf["pattern"],
                    gap_type=GapType(rf["gap_type"]),
                    severity_presumption=GapSeverity(rf["severity_presumption"]),
                    relevant_article=rf["relevant_article"],
                    rationale=rf.get("rationale", ""),
                )
                for rf in gp.get("red_flags", [])
            ],
            interpretive_authority=gp.get("interpretive_authority", []),
            cross_cutting=gp.get("cross_cutting", True),
            notes=gp.get("notes", ""),
        )
        articles[3] = art3

    # Numbered articles list
    for entry in raw.get("articles", []):
        art = _parse_article(entry)
        articles[art.number] = art

    return articles


def _load_general_comments() -> dict[str, GeneralComment]:
    """Load all General Comments from ``data/crpd/general_comments.json``."""
    with open(_CRPD_PATH / "general_comments.json", encoding="utf-8") as f:
        raw = json.load(f)
    return {
        gc["id"]: GeneralComment(
            id=gc["id"],
            number=gc["number"],
            article_addressed=gc["article_addressed"],
            title=gc["title"],
            year=gc["year"],
            document_symbol=gc["document_symbol"],
            key_holdings=gc.get("key_holdings", []),
            binding_force=BindingForce(gc.get("binding_force", "authoritative_interpretation")),
            url=gc.get("url", ""),
        )
        for gc in raw["general_comments"]
    }


def _load_principles() -> list[CRPDPrinciple]:
    """Load Art. 3 general principles."""
    with open(_CRPD_PATH / "articles.json", encoding="utf-8") as f:
        raw = json.load(f)
    return [
        CRPDPrinciple(
            label=p["label"],
            text=p["text"],
            article_subparagraph=p["subparagraph"],
        )
        for p in raw.get("general_principles", {}).get("principles", [])
    ]


# Module-level singletons
ARTICLES: dict[int, CRPDArticle] = _load_articles()
GENERAL_COMMENTS: dict[str, GeneralComment] = _load_general_comments()
PRINCIPLES: list[CRPDPrinciple] = _load_principles()


# ---------------------------------------------------------------------------
# Public accessor functions (pure)
# ---------------------------------------------------------------------------


def get_article(article_number: int) -> CRPDArticle:
    """Retrieve a CRPD article by number.

    Parameters
    ----------
    article_number:
        CRPD article number.

    Returns
    -------
    CRPDArticle

    Raises
    ------
    KeyError
        If the article number is not in the loaded corpus. Note that
        not all 50 CRPD articles are encoded in v2.0 — only the key
        analytical articles for the disability rights pilot.
    """
    if article_number not in ARTICLES:
        raise KeyError(
            f"CRPD Article {article_number} is not in the v2.0 corpus. "
            "Full article coverage is planned for v3.0."
        )
    return ARTICLES[article_number]


def get_minimum_standard(article_number: int) -> list[MinimumStandard]:
    """Return the minimum standards for a CRPD article.

    Parameters
    ----------
    article_number:
        CRPD article number.

    Returns
    -------
    list[MinimumStandard]
    """
    return get_article(article_number).minimum_standards


def get_red_flags(article_number: int) -> list[RedFlag]:
    """Return the red flags for a CRPD article.

    Red flags are legislative patterns that presumptively indicate
    non-compliance. They trigger deeper analysis, not automatic
    classification.

    Parameters
    ----------
    article_number:
        CRPD article number.

    Returns
    -------
    list[RedFlag]
    """
    return get_article(article_number).red_flags


def get_general_comment(gc_id: str) -> GeneralComment:
    """Retrieve a General Comment by ID.

    Parameters
    ----------
    gc_id:
        General Comment ID, e.g. 'GC_1', 'GC_2', ..., 'GC_6'.

    Returns
    -------
    GeneralComment

    Raises
    ------
    KeyError
        If the GC ID is not in the corpus.
    """
    if gc_id not in GENERAL_COMMENTS:
        raise KeyError(
            f"General Comment '{gc_id}' not found. "
            f"Available: {list(GENERAL_COMMENTS.keys())}"
        )
    return GENERAL_COMMENTS[gc_id]


def articles_for_obligation_type(obligation_type: ObligationType) -> list[CRPDArticle]:
    """Return all loaded articles generating a given obligation type.

    Parameters
    ----------
    obligation_type:
        An ``ObligationType`` enum value.

    Returns
    -------
    list[CRPDArticle]
    """
    return [a for a in ARTICLES.values() if obligation_type in a.obligation_types]


def cross_cutting_articles() -> list[CRPDArticle]:
    """Return all cross-cutting CRPD articles.

    Cross-cutting articles (Arts. 3, 4, 5, 9, 33) generate obligations
    that apply throughout all substantive articles. They should be assessed
    first in Stage 3 (conventionality analysis).
    """
    return [a for a in ARTICLES.values() if a.cross_cutting]


def articles_with_general_comment() -> list[CRPDArticle]:
    """Return articles that have at least one associated General Comment.

    General Comments are primary interpretive authorities. Articles with
    General Comments should be analysed with greater precision.
    """
    return [a for a in ARTICLES.values() if a.interpretive_authority]


def list_available_articles() -> list[int]:
    """Return the sorted list of article numbers available in the corpus."""
    return sorted(ARTICLES.keys())
