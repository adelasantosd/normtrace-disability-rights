"""
normtrace.criteria
==================
Analytical criteria as structured objects.

Criteria are the unit of analysis in NormTrace Stages 2 and 3. Each criterion
is a question posed to the domestic legal instrument. This module loads
criteria from the data files and exposes them as structured Python objects
with pure application functions.

The design separation is critical:
- Data files define *what* to look for (the analytical criteria).
- This module loads them as objects and provides *how* to apply them.
- The LLM receives criterion objects and returns ``CriterionResult`` instances.
- Scoring functions in ``normtrace.scoring`` aggregate results.

References
----------
Gender criteria: NormTrace exclusion-analysis framework; CRPD Art. 6;
CRPD Committee GC No. 3 (2016), CRPD/C/GC/3.

Intersectionality methodology: Crenshaw, K. (1989), 'Demarginalising the
intersection of race and sex', University of Chicago Legal Forum, 139–167;
CRPD Committee GC No. 6 (2018), CRPD/C/GC/6.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from normtrace.models import (
    AnalyticalCriterion,
    AnalyticalStage,
    CriterionResult,
    IntersectionalityAxis,
)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

_FRAMEWORKS_PATH = Path(__file__).parent.parent / "data" / "frameworks"


def _load_gender_criteria() -> list[AnalyticalCriterion]:
    path = _FRAMEWORKS_PATH / "gender_criteria.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [
        AnalyticalCriterion(
            id=c["id"],
            stage=AnalyticalStage(c["stage"]),
            dimension=c["dimension"],
            question=c["question"],
            positive_indicators=c["positive_indicators"],
            negative_indicators=c["negative_indicators"],
            applicable_articles=c.get("applicable_articles", []),
            weight=c.get("weight", 1.0),
            rationale=c.get("rationale", ""),
        )
        for c in data["criteria"]
    ]


def _load_intersectionality_axes() -> list[dict]:
    path = _FRAMEWORKS_PATH / "intersectionality_axes.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["axes"]


# Module-level singletons (loaded once at import)
GENDER_CRITERIA: list[AnalyticalCriterion] = _load_gender_criteria()
INTERSECTIONALITY_AXES: list[dict] = _load_intersectionality_axes()


# ---------------------------------------------------------------------------
# CriterionSet: a named, ordered collection of criteria
# ---------------------------------------------------------------------------


@dataclass
class CriterionSet:
    """An ordered, named collection of AnalyticalCriteria.

    CriterionSets are the unit passed to the LLM extraction component.
    The LLM applies each criterion in the set to the domestic text and
    returns a list of CriterionResult objects in the same order.
    """
    name: str
    stage: AnalyticalStage
    description: str
    criteria: list[AnalyticalCriterion]

    def get_criterion(self, criterion_id: str) -> AnalyticalCriterion:
        """Retrieve a criterion by its ID.

        Raises
        ------
        KeyError
            If no criterion with the given ID exists in this set.
        """
        for c in self.criteria:
            if c.id == criterion_id:
                return c
        raise KeyError(
            f"Criterion '{criterion_id}' not found in CriterionSet '{self.name}'."
        )

    def ids(self) -> list[str]:
        """Return the list of criterion IDs in this set."""
        return [c.id for c in self.criteria]

    def total_weight(self) -> float:
        """Return the sum of all criterion weights."""
        return sum(c.weight for c in self.criteria)


def build_gender_criterion_set() -> CriterionSet:
    """Build the standard gender perspective CriterionSet for Stage 2.

    Returns
    -------
    CriterionSet
        Ten gender diagnostic criteria, loaded from
        ``data/frameworks/gender_criteria.json``.
    """
    return CriterionSet(
        name="gender_perspective",
        stage=AnalyticalStage.EXCLUSION,
        description=(
            "Ten diagnostic criteria for assessing the gender perspective "
            "in a domestic legal instrument. Source: NormTrace Stage 2; "
            "CRPD Art. 6; CRPD Committee GC No. 3 (2016)."
        ),
        criteria=GENDER_CRITERIA,
    )


def build_intersectionality_criterion_set(
    axes: Optional[list[IntersectionalityAxis]] = None,
) -> CriterionSet:
    """Build an intersectionality CriterionSet for Stage 2.

    Each intersectionality axis is converted to an AnalyticalCriterion
    with the axis's diagnostic question, positive indicators (exclusion
    mechanisms absent), and negative indicators (exclusion mechanisms present).

    Parameters
    ----------
    axes:
        Optional list of axes to include. If None, all eight axes are included.

    Returns
    -------
    CriterionSet
    """
    selected_ids = (
        {a.value for a in axes} if axes else {a["id"] for a in INTERSECTIONALITY_AXES}
    )
    criteria = []
    for ax in INTERSECTIONALITY_AXES:
        if ax["id"] not in selected_ids:
            continue
        criteria.append(
            AnalyticalCriterion(
                id=f"intersect_{ax['id']}",
                stage=AnalyticalStage.EXCLUSION,
                dimension="intersectionality",
                question=ax["diagnostic_question"],
                positive_indicators=[
                    f"Absent: {mech}" for mech in ax["exclusion_mechanisms"]
                ],
                negative_indicators=ax["exclusion_mechanisms"],
                applicable_articles=ax.get("applicable_articles", []),
                weight=ax.get("weight", 1.0),
                rationale=f"Intersectionality axis: {ax['label']}. "
                f"Subgroup: {ax['subgroup']}",
            )
        )
    return CriterionSet(
        name="intersectionality",
        stage=AnalyticalStage.EXCLUSION,
        description=(
            "Intersectionality analysis criteria for Stage 2. Each criterion "
            "corresponds to one axis of intersectional disadvantage. Source: "
            "NormTrace exclusion-analysis framework; GC No. 6 (2018)."
        ),
        criteria=criteria,
    )


# ---------------------------------------------------------------------------
# Pure application functions
# ---------------------------------------------------------------------------


def apply_criteria(
    criterion_set: CriterionSet,
    results: list[CriterionResult],
) -> dict[str, CriterionResult]:
    """Index CriterionResults by criterion ID and validate completeness.

    This function is the bridge between the LLM extraction layer (which
    returns results) and the scoring layer (which needs results indexed
    by criterion ID).

    Parameters
    ----------
    criterion_set:
        The CriterionSet that was applied.
    results:
        List of CriterionResult instances returned by the LLM extraction
        component.

    Returns
    -------
    dict[str, CriterionResult]
        Mapping from criterion ID to result.

    Raises
    ------
    ValueError
        If a result references a criterion ID not in the criterion set.
    """
    criterion_ids = set(criterion_set.ids())
    indexed: dict[str, CriterionResult] = {}
    for result in results:
        if result.criterion_id not in criterion_ids:
            raise ValueError(
                f"Result references unknown criterion ID '{result.criterion_id}' "
                f"not in CriterionSet '{criterion_set.name}'."
            )
        indexed[result.criterion_id] = result
    return indexed


def check_gender_dimension(
    results: list[CriterionResult],
    threshold_satisfied: int = 4,
) -> bool:
    """Determine whether a domestic instrument has an adequate gender perspective.

    An instrument is considered to have an adequate gender dimension if at
    least ``threshold_satisfied`` of the gender criteria are satisfied.
    The default threshold of 4 out of 10 is conservative; stricter review
    should use a higher threshold.

    Parameters
    ----------
    results:
        CriterionResult list from applying ``build_gender_criterion_set()``.
    threshold_satisfied:
        Minimum number of satisfied criteria to return True. Default: 4.

    Returns
    -------
    bool
    """
    return sum(1 for r in results if r.satisfied is True) >= threshold_satisfied


def check_intersectionality(
    results: list[CriterionResult],
    axis: Optional[IntersectionalityAxis] = None,
) -> dict[str, Optional[bool]]:
    """Return satisfaction status for each intersectionality axis.

    Parameters
    ----------
    results:
        CriterionResult list from applying ``build_intersectionality_criterion_set()``.
    axis:
        If specified, return result for that axis only.

    Returns
    -------
    dict[str, Optional[bool]]
        Mapping from axis ID (without 'intersect_' prefix) to satisfied status.
    """
    mapping: dict[str, Optional[bool]] = {}
    for r in results:
        ax_id = r.criterion_id.removeprefix("intersect_")
        if axis is None or ax_id == axis.value:
            mapping[ax_id] = r.satisfied
    return mapping


def score_criterion_set(
    criterion_set: CriterionSet,
    indexed_results: dict[str, CriterionResult],
) -> float:
    """Compute a weighted compliance score for a CriterionSet.

    The score is the weighted proportion of satisfied criteria:

        score = sum(weight_i if satisfied_i) / sum(weight_i)

    Criteria with ``satisfied = None`` (insufficient information) are
    treated as unsatisfied for scoring purposes.

    Parameters
    ----------
    criterion_set:
        The CriterionSet that was applied.
    indexed_results:
        Indexed results from ``apply_criteria()``.

    Returns
    -------
    float
        Compliance score in [0.0, 1.0]. 1.0 = all criteria satisfied.
    """
    total_weight = criterion_set.total_weight()
    if total_weight == 0:
        return 0.0
    satisfied_weight = sum(
        c.weight
        for c in criterion_set.criteria
        if indexed_results.get(c.id) and indexed_results[c.id].satisfied is True
    )
    return satisfied_weight / total_weight


def unsatisfied_criteria(
    criterion_set: CriterionSet,
    indexed_results: dict[str, CriterionResult],
) -> list[AnalyticalCriterion]:
    """Return the list of unsatisfied or unassessed criteria.

    Useful for generating targeted reform recommendations: each unsatisfied
    criterion corresponds to a specific legislative gap.

    Returns
    -------
    list[AnalyticalCriterion]
        Criteria where the result is False or None.
    """
    return [
        c
        for c in criterion_set.criteria
        if not (
            indexed_results.get(c.id) and indexed_results[c.id].satisfied is True
        )
    ]
