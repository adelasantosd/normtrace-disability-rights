"""
normtrace.references
====================
Reference management: loading, lookup, and citation generation.

The NormTrace reference corpus (jurisprudence, doctrine, international
instruments) is stored in ``data/references/`` as structured JSON files.
This module loads the corpus and exposes pure functions for looking up
references and generating formatted citations.

Design principle
----------------
All interpretive claims in NormTrace outputs must be traceable to a
reference in this corpus. Fabrication of case law or treaty provisions
is a non-negotiable analytical rule (NormTrace protocol, Rule 1).
The corpus is the constraint.

References
----------
Corpus compiled from: OHCHR treaty body documents; UN treaty collection;
SCJN jurisprudential database; Federal Supreme Court of Switzerland;
IACtHR jurisprudence series; doctrinal bibliography.
"""

from __future__ import annotations

import json
from pathlib import Path

from normtrace.models import (
    BindingForce,
    DoctrinalReference,
    LegalReference,
    ReferenceType,
)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

_REFS_PATH = Path(__file__).parent.parent / "data" / "references"


def _load_jurisprudence() -> list[LegalReference]:
    with open(_REFS_PATH / "jurisprudence.json", encoding="utf-8") as f:
        data = json.load(f)
    return [
        LegalReference(
            id=r["id"],
            reference_type=ReferenceType(r["reference_type"]),
            title=r["title"],
            year=r["year"],
            binding_force=BindingForce(r["binding_force"]),
            court_or_body=r.get("court_or_body", ""),
            document_symbol=r.get("document_symbol", ""),
            jurisdiction=r.get("jurisdiction", ""),
            url=r.get("url", ""),
            key_holdings=r.get("key_holdings", []),
            relevant_articles=r.get("relevant_articles", []),
            notes=r.get("notes", ""),
        )
        for r in data["jurisprudence"]
    ]


def _load_doctrine() -> list[DoctrinalReference]:
    with open(_REFS_PATH / "doctrine.json", encoding="utf-8") as f:
        data = json.load(f)
    return [
        DoctrinalReference(
            id=r["id"],
            authors=r["authors"],
            title=r["title"],
            year=r["year"],
            publication=r["publication"],
            pages=r.get("pages", ""),
            doi=r.get("doi", ""),
            url=r.get("url", ""),
            relevance=r.get("relevance", ""),
        )
        for r in data["doctrine"]
    ]


# Module-level corpus (loaded once at import)
JURISPRUDENCE: list[LegalReference] = _load_jurisprudence()
DOCTRINE: list[DoctrinalReference] = _load_doctrine()

# Combined index by ID
_JURI_INDEX: dict[str, LegalReference] = {r.id: r for r in JURISPRUDENCE}
_DOCT_INDEX: dict[str, DoctrinalReference] = {r.id: r for r in DOCTRINE}


# ---------------------------------------------------------------------------
# Lookup functions (pure)
# ---------------------------------------------------------------------------


def get_legal_reference(ref_id: str) -> LegalReference:
    """Retrieve a legal reference by its ID.

    Parameters
    ----------
    ref_id:
        Reference ID as defined in the corpus JSON files,
        e.g. 'IACtHR_Almonacid_2006', 'CRPD_CO_MEX_2014'.

    Returns
    -------
    LegalReference

    Raises
    ------
    KeyError
        If the ID is not found in the jurisprudence corpus.
    """
    if ref_id not in _JURI_INDEX:
        raise KeyError(
            f"Legal reference '{ref_id}' not found in corpus. "
            "Do not fabricate references not present in the corpus."
        )
    return _JURI_INDEX[ref_id]


def get_doctrinal_reference(ref_id: str) -> DoctrinalReference:
    """Retrieve a doctrinal reference by its ID.

    Raises
    ------
    KeyError
        If the ID is not found in the doctrine corpus.
    """
    if ref_id not in _DOCT_INDEX:
        raise KeyError(f"Doctrinal reference '{ref_id}' not found in corpus.")
    return _DOCT_INDEX[ref_id]


def references_for_article(article_number: int) -> list[LegalReference]:
    """Return all legal references relevant to a given CRPD article number.

    Parameters
    ----------
    article_number:
        CRPD article number (1–50).

    Returns
    -------
    list[LegalReference]
        All references in the corpus where ``relevant_articles`` contains
        the given article number.
    """
    return [r for r in JURISPRUDENCE if article_number in r.relevant_articles]


def references_for_jurisdiction(jurisdiction_code: str) -> list[LegalReference]:
    """Return all legal references for a given jurisdiction.

    Parameters
    ----------
    jurisdiction_code:
        ISO 3166-1 alpha-2 code ('MX', 'CH') or 'INT' for international.

    Returns
    -------
    list[LegalReference]
    """
    return [
        r
        for r in JURISPRUDENCE
        if r.jurisdiction == jurisdiction_code or r.jurisdiction == "INT"
    ]


def concluding_observations_for_jurisdiction(
    jurisdiction_code: str,
) -> list[LegalReference]:
    """Return CRPD Committee concluding observations for a jurisdiction.

    Parameters
    ----------
    jurisdiction_code:
        ISO 3166-1 alpha-2 code.
    """
    return [
        r
        for r in JURISPRUDENCE
        if r.reference_type == ReferenceType.CONCLUDING_OBSERVATIONS
        and r.jurisdiction == jurisdiction_code
    ]


def binding_references(jurisdiction_code: str) -> list[LegalReference]:
    """Return only binding (not merely persuasive) references for a jurisdiction.

    Useful for distinguishing between arguments that rely on binding
    authority vs. persuasive authority when drafting litigation briefs.
    """
    return [
        r
        for r in references_for_jurisdiction(jurisdiction_code)
        if r.binding_force
        in (BindingForce.BINDING_TREATY, BindingForce.BINDING_DOMESTIC)
    ]


def doctrine_for_domain(domain: str) -> list[DoctrinalReference]:
    """Return doctrinal references for a given theoretical domain.

    Parameters
    ----------
    domain:
        Domain string as defined in ``doctrine.json``, e.g.
        'intersectionality', 'legal_capacity', 'social_model_disability',
        'conventionality_control'.
    """
    # domain is stored in the raw JSON but not in DoctrinalReference dataclass;
    # reload raw data for domain filtering
    with open(_REFS_PATH / "doctrine.json", encoding="utf-8") as f:
        raw = json.load(f)
    ids = {r["id"] for r in raw["doctrine"] if r.get("domain") == domain}
    return [r for r in DOCTRINE if r.id in ids]


# ---------------------------------------------------------------------------
# Citation generation (pure)
# ---------------------------------------------------------------------------


def generate_citation(ref_id: str, style: str = "legal") -> str:
    """Generate a formatted citation for a reference.

    Parameters
    ----------
    ref_id:
        Reference ID from the corpus.
    style:
        Citation style: 'legal' (default), 'apa', or 'short'.

    Returns
    -------
    str
        Formatted citation string.

    Raises
    ------
    KeyError
        If the reference ID is not found in either corpus.
    """
    # Try jurisprudence first, then doctrine
    if ref_id in _JURI_INDEX:
        return _format_legal_reference(_JURI_INDEX[ref_id], style)
    if ref_id in _DOCT_INDEX:
        return _format_doctrinal_reference(_DOCT_INDEX[ref_id], style)
    raise KeyError(f"Reference '{ref_id}' not found in corpus.")


def _format_legal_reference(ref: LegalReference, style: str) -> str:
    """Format a LegalReference as a citation string."""
    if style == "short":
        sym = f" [{ref.document_symbol}]" if ref.document_symbol else ""
        return f"{ref.title} ({ref.year}){sym}"
    if style == "apa":
        body = f"{ref.court_or_body}. " if ref.court_or_body else ""
        sym = f" ({ref.document_symbol})" if ref.document_symbol else ""
        return f"{body}({ref.year}). {ref.title}{sym}."
    # Default: legal style
    body = f"{ref.court_or_body}, " if ref.court_or_body else ""
    sym = f", {ref.document_symbol}" if ref.document_symbol else ""
    url = f" Available at: {ref.url}" if ref.url else ""
    return f"{body}{ref.title} ({ref.year}){sym}.{url}"


def _format_doctrinal_reference(ref: DoctrinalReference, style: str) -> str:
    """Format a DoctrinalReference as a citation string."""
    authors = " and ".join(ref.authors)
    if style == "short":
        last = ref.authors[0].split(",")[0] if ref.authors else "Unknown"
        return f"{last} ({ref.year})"
    if style == "apa":
        pages = f", pp. {ref.pages}" if ref.pages else ""
        doi = f" https://doi.org/{ref.doi}" if ref.doi else ""
        return (
            f"{authors} ({ref.year}). {ref.title}. {ref.publication}{pages}.{doi}"
        )
    # Default: legal style
    pages = f", pp. {ref.pages}" if ref.pages else ""
    return f"{authors}, '{ref.title}', {ref.publication} ({ref.year}){pages}."
