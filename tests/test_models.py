"""
Tests for normtrace.models
===========================
Verify that core dataclasses are instantiable, immutable where declared,
and that all enum values are well-formed.

No LLM calls. No I/O. Pure unit tests.
"""

import pytest
from normtrace.models import (
    AnalyticalStage,
    BindingForce,
    CRPDArticle,
    CriterionResult,
    GapFinding,
    GapSeverity,
    GapType,
    InstrumentMetadata,
    IntersectionalityAxis,
    JurisdictionType,
    MinimumStandard,
    ObligationType,
    RedFlag,
    ReferenceType,
)


class TestEnums:
    def test_gap_type_values(self):
        expected = {
            "total_absence", "weak_recognition", "incompatibility",
            "regression", "structural_discrimination", "implementation_gap",
            "normative_silence", "declaratory_only",
        }
        assert {g.value for g in GapType} == expected

    def test_gap_severity_values(self):
        expected = {"critical", "high", "medium", "low", "uncertain"}
        assert {s.value for s in GapSeverity} == expected

    def test_obligation_type_values(self):
        assert {o.value for o in ObligationType} == {"respect", "protect", "fulfil"}

    def test_intersectionality_axis_count(self):
        assert len(IntersectionalityAxis) == 8

    def test_analytical_stage_count(self):
        assert len(AnalyticalStage) == 5

    def test_jurisdiction_type_values(self):
        values = {j.value for j in JurisdictionType}
        assert "conventionality_control" in values
        assert "international_compatibility_analysis" in values


class TestMinimumStandard:
    def test_instantiation(self):
        ms = MinimumStandard(
            description="Test standard",
            source_article=12,
            source_paragraphs=["12(2)"],
            general_comment_ids=["GC_1"],
        )
        assert ms.source_article == 12
        assert "12(2)" in ms.source_paragraphs

    def test_frozen(self):
        ms = MinimumStandard(description="Test", source_article=5)
        with pytest.raises(Exception):  # frozen dataclass raises FrozenInstanceError
            ms.source_article = 6  # type: ignore


class TestRedFlag:
    def test_instantiation(self):
        rf = RedFlag(
            pattern="Guardianship provisions",
            gap_type=GapType.INCOMPATIBILITY,
            severity_presumption=GapSeverity.CRITICAL,
            relevant_article=12,
            rationale="GC No. 1 (2014) prohibits substituted decision-making.",
        )
        assert rf.gap_type == GapType.INCOMPATIBILITY
        assert rf.severity_presumption == GapSeverity.CRITICAL

    def test_frozen(self):
        rf = RedFlag(
            pattern="Test",
            gap_type=GapType.TOTAL_ABSENCE,
            severity_presumption=GapSeverity.HIGH,
            relevant_article=9,
        )
        with pytest.raises(Exception):
            rf.relevant_article = 12  # type: ignore


class TestGapFinding:
    def test_default_instantiation(self):
        f = GapFinding(jurisdiction="MX")
        assert f.gap_type is None
        assert f.gap_severity is None
        assert f.article_number is None
        assert f.subgroup_affected == []

    def test_full_instantiation(self):
        f = GapFinding(
            jurisdiction="CH",
            domestic_legal_instrument="Zivilgesetzbuch (ZGB)",
            legal_instrument_type="federal statute",
            gap_type=GapType.INCOMPATIBILITY,
            gap_severity=GapSeverity.CRITICAL,
            article_number=12,
            gap_description="ZGB Art. 390 curatorship constitutes substituted decision-making incompatible with CRPD Art. 12.",
            rights_holder_group="persons with disabilities",
            language_model="mixed",
            evidence_excerpts=["Art. 390 ZGB: ..."],
        )
        assert f.gap_type == GapType.INCOMPATIBILITY
        assert f.gap_severity == GapSeverity.CRITICAL
        assert f.jurisdiction == "CH"

    def test_mutable(self):
        """GapFinding is mutable — it is progressively filled during analysis."""
        f = GapFinding(jurisdiction="MX")
        f.gap_type = GapType.TOTAL_ABSENCE
        assert f.gap_type == GapType.TOTAL_ABSENCE


class TestInstrumentMetadata:
    def test_instantiation(self):
        m = InstrumentMetadata(
            jurisdiction="MX",
            instrument_name="Ley General para la Inclusión de las Personas con Discapacidad",
            instrument_type="federal statute",
            date_of_version="2011",
            is_current=True,
            completeness_verified=True,
            currency_verified=True,
        )
        assert m.jurisdiction == "MX"
        assert m.is_current is True

    def test_uncertainty_default(self):
        """is_current and currency_verified default to None/False — not assumed."""
        m = InstrumentMetadata(
            jurisdiction="CH",
            instrument_name="Test",
            instrument_type="cantonal statute",
            date_of_version=None,
        )
        assert m.is_current is None
        assert m.currency_verified is False
        assert m.completeness_verified is False


class TestCriterionResult:
    def test_uncertain_result(self):
        r = CriterionResult(
            criterion_id="gender_01",
            satisfied=None,
            confidence=0.3,
            notes="Text is ambiguous on this point.",
        )
        assert r.satisfied is None
        assert r.confidence < 1.0

    def test_positive_result(self):
        r = CriterionResult(
            criterion_id="gender_04",
            satisfied=True,
            evidence_excerpt="Art. 18: The State shall protect women with disabilities from all forms of violence.",
            confidence=0.9,
        )
        assert r.satisfied is True
