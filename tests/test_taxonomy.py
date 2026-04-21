"""
Tests for normtrace.taxonomy
=============================
Verify gap classification, severity scoring, priority scoring, and
aggregate assessment functions. All tests are pure (no LLM, no I/O
beyond the initial data load at module import).
"""

import pytest
from normtrace.models import GapFinding, GapSeverity, GapType
from normtrace.taxonomy import (
    SEVERITY_WEIGHTS,
    AggregateAssessment,
    SeverityAssessment,
    aggregate_assessment,
    compute_priority_score,
    default_severity,
    describe_gap_type,
    get_diagnostic_indicators,
    prioritize_gaps,
    score_gap_severity,
)


class TestSeverityWeights:
    def test_all_levels_present(self):
        for level in (GapSeverity.CRITICAL, GapSeverity.HIGH, GapSeverity.MEDIUM, GapSeverity.LOW):
            assert level in SEVERITY_WEIGHTS

    def test_ordering(self):
        assert SEVERITY_WEIGHTS[GapSeverity.CRITICAL] > SEVERITY_WEIGHTS[GapSeverity.HIGH]
        assert SEVERITY_WEIGHTS[GapSeverity.HIGH] > SEVERITY_WEIGHTS[GapSeverity.MEDIUM]
        assert SEVERITY_WEIGHTS[GapSeverity.MEDIUM] > SEVERITY_WEIGHTS[GapSeverity.LOW]
        assert SEVERITY_WEIGHTS[GapSeverity.LOW] >= 1


class TestDefaultSeverity:
    def test_incompatibility_is_critical(self):
        assert default_severity(GapType.INCOMPATIBILITY) == GapSeverity.CRITICAL

    def test_total_absence_is_high(self):
        assert default_severity(GapType.TOTAL_ABSENCE) == GapSeverity.HIGH

    def test_weak_recognition_is_medium(self):
        assert default_severity(GapType.WEAK_RECOGNITION) == GapSeverity.MEDIUM

    def test_declaratory_only_is_medium(self):
        assert default_severity(GapType.DECLARATORY_ONLY) == GapSeverity.MEDIUM


class TestDescribeGapType:
    def test_returns_non_empty_string(self):
        for gap_type in GapType:
            description = describe_gap_type(gap_type)
            assert isinstance(description, str)
            assert len(description) > 10

    def test_incompatibility_mentions_contradicts(self):
        desc = describe_gap_type(GapType.INCOMPATIBILITY).lower()
        assert "contradict" in desc or "irreconcilable" in desc or "contrary" in desc


class TestGetDiagnosticIndicators:
    def test_returns_dict_with_positive_negative(self):
        indicators = get_diagnostic_indicators(GapType.NORMATIVE_SILENCE)
        assert "positive" in indicators
        assert "negative" in indicators
        assert isinstance(indicators["positive"], list)
        assert len(indicators["positive"]) > 0


class TestScoreGapSeverity:
    def test_no_modifiers_returns_default(self):
        result = score_gap_severity(GapType.WEAK_RECOGNITION)
        assert result.base_severity == GapSeverity.MEDIUM
        assert result.final_severity == GapSeverity.MEDIUM
        assert result.modifiers_applied == []

    def test_immediately_applicable_upgrades_severity(self):
        # WEAK_RECOGNITION (medium) + immediately applicable -> HIGH
        result = score_gap_severity(
            GapType.WEAK_RECOGNITION,
            is_immediately_applicable=True,
        )
        assert result.final_severity == GapSeverity.HIGH
        assert any("immediately applicable" in m for m in result.modifiers_applied)

    def test_intersectional_upgrades_severity(self):
        result = score_gap_severity(
            GapType.NORMATIVE_SILENCE,
            is_intersectional=True,
        )
        assert result.final_severity.value in ("high", "critical")

    def test_alternative_coverage_downgrades(self):
        result = score_gap_severity(
            GapType.TOTAL_ABSENCE,
            has_alternative_coverage=True,
        )
        # HIGH -> MEDIUM with alternative coverage
        assert result.final_severity == GapSeverity.MEDIUM

    def test_critical_not_upgraded_further(self):
        """CRITICAL is the ceiling; no modifier can go higher."""
        result = score_gap_severity(
            GapType.INCOMPATIBILITY,
            is_immediately_applicable=True,
            is_intersectional=True,
        )
        assert result.final_severity == GapSeverity.CRITICAL

    def test_narrow_scope_downgrades(self):
        result = score_gap_severity(
            GapType.TOTAL_ABSENCE,
            scope="narrow",
        )
        assert result.final_severity == GapSeverity.MEDIUM

    def test_numeric_score_consistent_with_level(self):
        result = score_gap_severity(GapType.INCOMPATIBILITY)
        assert result.numeric_score == SEVERITY_WEIGHTS[GapSeverity.CRITICAL]


class TestComputePriorityScore:
    def test_maximum_score(self):
        score = compute_priority_score(3, 3, 3, 3)
        assert score == 12

    def test_minimum_score(self):
        score = compute_priority_score(1, 1, 1, 1)
        assert score == 4

    def test_invalid_factor_raises(self):
        with pytest.raises(ValueError, match="urgency"):
            compute_priority_score(0, 2, 2, 2)
        with pytest.raises(ValueError, match="systemic_impact"):
            compute_priority_score(2, 2, 2, 4)

    def test_midpoint(self):
        score = compute_priority_score(2, 2, 2, 2)
        assert score == 8


class TestPrioritizeGaps:
    def _make_finding(self, severity: GapSeverity) -> GapFinding:
        f = GapFinding(jurisdiction="MX")
        f.gap_severity = severity
        return f

    def test_sorts_critical_first(self):
        findings = [
            self._make_finding(GapSeverity.LOW),
            self._make_finding(GapSeverity.CRITICAL),
            self._make_finding(GapSeverity.MEDIUM),
            self._make_finding(GapSeverity.HIGH),
        ]
        sorted_findings = prioritize_gaps(findings)
        assert sorted_findings[0].gap_severity == GapSeverity.CRITICAL
        assert sorted_findings[-1].gap_severity == GapSeverity.LOW

    def test_stable_sort_within_same_severity(self):
        f1 = GapFinding(jurisdiction="MX")
        f1.gap_severity = GapSeverity.HIGH
        f1.gap_description = "first"
        f2 = GapFinding(jurisdiction="MX")
        f2.gap_severity = GapSeverity.HIGH
        f2.gap_description = "second"
        sorted_findings = prioritize_gaps([f1, f2])
        assert sorted_findings[0].gap_description == "first"


class TestAggregateAssessment:
    def _make_finding(self, gap_type: GapType, severity: GapSeverity) -> GapFinding:
        f = GapFinding(jurisdiction="MX")
        f.gap_type = gap_type
        f.gap_severity = severity
        return f

    def test_insufficient_data_for_few_findings(self):
        findings = [self._make_finding(GapType.TOTAL_ABSENCE, GapSeverity.HIGH)]
        result = aggregate_assessment(findings)
        assert result.overall_alignment == "insufficient_data"

    def test_non_aligned_with_critical(self):
        findings = [
            self._make_finding(GapType.INCOMPATIBILITY, GapSeverity.CRITICAL),
            self._make_finding(GapType.NORMATIVE_SILENCE, GapSeverity.MEDIUM),
            self._make_finding(GapType.WEAK_RECOGNITION, GapSeverity.LOW),
        ]
        result = aggregate_assessment(findings)
        assert result.overall_alignment == "non_aligned"
        assert result.critical_count == 1

    def test_partially_aligned_with_high(self):
        findings = [
            self._make_finding(GapType.TOTAL_ABSENCE, GapSeverity.HIGH),
            self._make_finding(GapType.NORMATIVE_SILENCE, GapSeverity.MEDIUM),
            self._make_finding(GapType.WEAK_RECOGNITION, GapSeverity.LOW),
        ]
        result = aggregate_assessment(findings)
        assert result.overall_alignment == "partially_aligned"

    def test_by_type_counts(self):
        findings = [
            self._make_finding(GapType.INCOMPATIBILITY, GapSeverity.CRITICAL),
            self._make_finding(GapType.INCOMPATIBILITY, GapSeverity.HIGH),
            self._make_finding(GapType.NORMATIVE_SILENCE, GapSeverity.MEDIUM),
        ]
        result = aggregate_assessment(findings)
        assert result.by_type.get("incompatibility") == 2
        assert result.by_type.get("normative_silence") == 1

    def test_weighted_severity_sum(self):
        findings = [
            self._make_finding(GapType.INCOMPATIBILITY, GapSeverity.CRITICAL),
            self._make_finding(GapType.TOTAL_ABSENCE, GapSeverity.HIGH),
            self._make_finding(GapType.WEAK_RECOGNITION, GapSeverity.MEDIUM),
        ]
        result = aggregate_assessment(findings)
        expected = (
            SEVERITY_WEIGHTS[GapSeverity.CRITICAL]
            + SEVERITY_WEIGHTS[GapSeverity.HIGH]
            + SEVERITY_WEIGHTS[GapSeverity.MEDIUM]
        )
        assert result.weighted_severity_sum == expected
