"""
normtrace.taxonomy
==================
Gap taxonomy: classification logic and severity scoring.

This module exposes the NormTrace gap taxonomy as deterministic Python
functions. All functions are pure (no I/O, no LLM calls) and fully testable.

The taxonomy is loaded from ``data/frameworks/gap_taxonomy.json`` at import
time. Classification and scoring functions operate on the in-memory taxonomy
object.

Architecture note
-----------------
The LLM extracts gap descriptions from domestic legal text and returns
``GapFinding`` instances with ``gap_type = None`` and ``gap_severity = None``.
The functions in this module assign those fields based on structured criteria,
keeping the classification logic independent of the language model.

References
----------
Gap taxonomy derived from: CRPD Committee, Concluding Observations to Mexico
(CRPD/C/MEX/CO/1, 2014) and Switzerland (CRPD/C/CHE/CO/1, 2022); NormTrace
analytical protocol v2.0.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from normtrace.models import GapFinding, GapSeverity, GapType

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

_DATA_PATH = Path(__file__).parent.parent / "data" / "frameworks" / "gap_taxonomy.json"


def _load_taxonomy() -> dict:
    with open(_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


_TAXONOMY: dict = _load_taxonomy()

# Pre-build severity weight map from the data file
SEVERITY_WEIGHTS: dict[GapSeverity, int] = {
    GapSeverity(k): v
    for k, v in _TAXONOMY["severity_weights"].items()
    if k in {s.value for s in GapSeverity}
}


# ---------------------------------------------------------------------------
# Classification helpers
# ---------------------------------------------------------------------------


def get_gap_type_definition(gap_type: GapType) -> dict:
    """Return the full taxonomy entry for a given GapType.

    Parameters
    ----------
    gap_type:
        A ``GapType`` enum value.

    Returns
    -------
    dict
        The raw taxonomy entry from ``gap_taxonomy.json``.

    Raises
    ------
    KeyError
        If the gap type has no entry in the taxonomy (should not occur
        unless the taxonomy file is incomplete).
    """
    for entry in _TAXONOMY["gap_types"]:
        if entry["id"] == gap_type.value:
            return entry
    raise KeyError(f"Gap type '{gap_type.value}' not found in taxonomy.")


def default_severity(gap_type: GapType) -> GapSeverity:
    """Return the default severity level for a gap type.

    The default severity is the severity assigned in the absence of
    modifying conditions. Severity modifiers must be applied separately
    using ``apply_severity_modifiers()``.

    Parameters
    ----------
    gap_type:
        A ``GapType`` enum value.

    Returns
    -------
    GapSeverity
        The default severity for the gap type.
    """
    entry = get_gap_type_definition(gap_type)
    return GapSeverity(entry["default_severity"])


def describe_gap_type(gap_type: GapType) -> str:
    """Return the human-readable definition of a gap type.

    Useful for generating readable analytical summaries and for
    communicating classification decisions to human reviewers.
    """
    return get_gap_type_definition(gap_type)["definition"]


def get_diagnostic_indicators(gap_type: GapType) -> dict[str, list[str]]:
    """Return the diagnostic indicators (positive and negative) for a gap type.

    Positive indicators signal presence of the gap type.
    Negative indicators signal the gap type is *not* present.

    Returns
    -------
    dict with keys 'positive' and 'negative', each a list of strings.
    """
    entry = get_gap_type_definition(gap_type)
    return entry["diagnostic_indicators"]


# ---------------------------------------------------------------------------
# Severity scoring
# ---------------------------------------------------------------------------


@dataclass
class SeverityAssessment:
    """Result of a severity scoring operation."""
    gap_type: GapType
    base_severity: GapSeverity
    final_severity: GapSeverity
    numeric_score: int
    modifiers_applied: list[str]


def score_gap_severity(
    gap_type: GapType,
    is_immediately_applicable: bool = False,
    is_intersectional: bool = False,
    has_alternative_coverage: bool = False,
    scope: str = "broad",
) -> SeverityAssessment:
    """Score the severity of a gap given its type and contextual modifiers.

    This function implements the severity modifier logic from the gap taxonomy.
    All inputs are structured (boolean, enum) so the function is fully testable
    without reference to any text or language model output.

    Parameters
    ----------
    gap_type:
        The classified gap type.
    is_immediately_applicable:
        True if the right is immediately applicable (not subject to
        progressive realisation). Immediately applicable rights: non-
        discrimination, legal capacity (Art. 12), liberty (Art. 14).
    is_intersectional:
        True if the gap affects an intersectional subgroup (e.g.,
        women with disabilities, indigenous persons with disabilities).
    has_alternative_coverage:
        True if the gap is partially addressed by a separate instrument
        or provision not under analysis.
    scope:
        'broad' (affects all or most persons with disabilities),
        'sectoral' (affects a sector or domain),
        'narrow' (affects a specific subgroup in a limited context).

    Returns
    -------
    SeverityAssessment
        Structured result including base severity, final severity,
        numeric score, and list of modifiers applied.
    """
    base = default_severity(gap_type)
    current = base
    modifiers: list[str] = []

    severity_order = [
        GapSeverity.LOW,
        GapSeverity.MEDIUM,
        GapSeverity.HIGH,
        GapSeverity.CRITICAL,
    ]

    def upgrade(s: GapSeverity) -> GapSeverity:
        idx = severity_order.index(s)
        return severity_order[min(idx + 1, len(severity_order) - 1)]

    def downgrade(s: GapSeverity) -> GapSeverity:
        idx = severity_order.index(s)
        return severity_order[max(idx - 1, 0)]

    if is_immediately_applicable and current != GapSeverity.CRITICAL:
        upgraded = upgrade(current)
        if upgraded != current:
            modifiers.append("upgraded: immediately applicable right")
            current = upgraded

    if is_intersectional and current not in (GapSeverity.CRITICAL,):
        upgraded = upgrade(current)
        if upgraded != current:
            modifiers.append("upgraded: intersectional impact")
            current = upgraded

    if has_alternative_coverage and current != GapSeverity.LOW:
        downgraded = downgrade(current)
        if downgraded != current:
            modifiers.append("downgraded: alternative coverage in separate instrument")
            current = downgraded

    if scope == "narrow" and current not in (GapSeverity.LOW, GapSeverity.MEDIUM):
        downgraded = downgrade(current)
        if downgraded != current:
            modifiers.append("downgraded: narrow scope")
            current = downgraded

    return SeverityAssessment(
        gap_type=gap_type,
        base_severity=base,
        final_severity=current,
        numeric_score=SEVERITY_WEIGHTS.get(current, 0),
        modifiers_applied=modifiers,
    )


def compute_priority_score(
    urgency: int,
    remediability: int,
    litigation_potential: int,
    systemic_impact: int,
) -> int:
    """Compute the priority score for a gap using the four-factor matrix.

    The priority score is the sum of the four factor scores (each 1–3),
    range: 4–12. Higher is higher priority. This is intentionally additive
    rather than multiplicative to avoid zero-score artefacts.

    Parameters
    ----------
    urgency:
        1–3 (3 = ongoing active harm).
    remediability:
        1–3 (3 = single amendment would remedy).
    litigation_potential:
        1–3 (3 = strong constitutional/conventional hook).
    systemic_impact:
        1–3 (3 = cross-cutting, affects all persons with disabilities).

    Returns
    -------
    int
        Priority score (4–12).

    Raises
    ------
    ValueError
        If any factor is outside the 1–3 range.
    """
    factors = {
        "urgency": urgency,
        "remediability": remediability,
        "litigation_potential": litigation_potential,
        "systemic_impact": systemic_impact,
    }
    for name, val in factors.items():
        if not (1 <= val <= 3):
            raise ValueError(
                f"Factor '{name}' must be between 1 and 3; got {val}."
            )
    return sum(factors.values())


def prioritize_gaps(findings: list[GapFinding]) -> list[GapFinding]:
    """Sort a list of GapFindings by severity (descending).

    Uses ``SEVERITY_WEIGHTS`` to order: CRITICAL > HIGH > MEDIUM > LOW > UNCERTAIN.
    Within the same severity level, ordering is stable (preserves input order).

    Parameters
    ----------
    findings:
        List of ``GapFinding`` instances.

    Returns
    -------
    list[GapFinding]
        Same findings sorted by severity descending.
    """
    return sorted(
        findings,
        key=lambda f: SEVERITY_WEIGHTS.get(f.gap_severity, 0)
        if f.gap_severity
        else 0,
        reverse=True,
    )


# ---------------------------------------------------------------------------
# Aggregate assessment
# ---------------------------------------------------------------------------


@dataclass
class AggregateAssessment:
    """Aggregate result of a NormTrace analysis over multiple gap findings."""
    total_findings: int
    by_type: dict[str, int]
    """Count of findings per GapType value."""
    by_severity: dict[str, int]
    """Count of findings per GapSeverity value."""
    critical_count: int
    high_count: int
    weighted_severity_sum: int
    """Sum of severity weights across all findings. Useful for cross-instrument comparison."""
    overall_alignment: str
    """'non_aligned', 'partially_aligned', 'aligned', or 'insufficient_data'."""


def aggregate_assessment(findings: list[GapFinding]) -> AggregateAssessment:
    """Produce an aggregate assessment from a list of GapFindings.

    This function is the final aggregation step in the NormTrace pipeline.
    It does not interpret findings — it counts and weights them.

    The ``overall_alignment`` heuristic:
    - 'non_aligned': any CRITICAL gap, OR more than 3 HIGH gaps
    - 'partially_aligned': 1–3 HIGH gaps and no CRITICAL gaps
    - 'aligned': only LOW or no gaps
    - 'insufficient_data': fewer than 3 findings (analysis incomplete)

    Parameters
    ----------
    findings:
        List of completed GapFinding instances.

    Returns
    -------
    AggregateAssessment
    """
    if len(findings) < 3:
        return AggregateAssessment(
            total_findings=len(findings),
            by_type={},
            by_severity={},
            critical_count=0,
            high_count=0,
            weighted_severity_sum=0,
            overall_alignment="insufficient_data",
        )

    by_type: dict[str, int] = {}
    by_severity: dict[str, int] = {}
    weighted_sum = 0
    critical = 0
    high = 0

    for f in findings:
        if f.gap_type:
            by_type[f.gap_type.value] = by_type.get(f.gap_type.value, 0) + 1
        if f.gap_severity:
            by_severity[f.gap_severity.value] = (
                by_severity.get(f.gap_severity.value, 0) + 1
            )
            weighted_sum += SEVERITY_WEIGHTS.get(f.gap_severity, 0)
            if f.gap_severity == GapSeverity.CRITICAL:
                critical += 1
            elif f.gap_severity == GapSeverity.HIGH:
                high += 1

    if critical > 0 or high > 3:
        alignment = "non_aligned"
    elif 1 <= high <= 3:
        alignment = "partially_aligned"
    elif all(
        f.gap_severity in (GapSeverity.LOW, None) for f in findings
    ):
        alignment = "aligned"
    else:
        alignment = "partially_aligned"

    return AggregateAssessment(
        total_findings=len(findings),
        by_type=by_type,
        by_severity=by_severity,
        critical_count=critical,
        high_count=high,
        weighted_severity_sum=weighted_sum,
        overall_alignment=alignment,
    )
