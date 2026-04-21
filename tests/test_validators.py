"""
Tests for normtrace.validators
================================
Verify that validation functions correctly enforce Stage 0 requirements,
epistemic consistency rules, and enforceability assessment heuristics.

All tests are pure — no LLM, no network I/O.
"""

import pytest
from normtrace.models import (
    GapFinding,
    GapSeverity,
    GapType,
    InstrumentMetadata,
)
from normtrace.validators import (
    STRONG_OBLIGATION_VERBS,
    WEAK_OBLIGATION_VERBS,
    assess_enforceability_markers,
    assess_obligation_verb,
    validate_findings_batch,
    validate_gap_finding,
    validate_instrument_metadata,
)


class TestValidateInstrumentMetadata:
    def test_valid_metadata_passes(self):
        m = InstrumentMetadata(
            jurisdiction="MX",
            instrument_name="Ley General para la Inclusión de las Personas con Discapacidad",
            instrument_type="federal statute",
            date_of_version="2011",
            is_current=True,
            completeness_verified=True,
            currency_verified=True,
            uncertainty_notes="",
        )
        result = validate_instrument_metadata(m)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_invalid_jurisdiction_code(self):
        m = InstrumentMetadata(
            jurisdiction="mexico",  # not ISO alpha-2
            instrument_name="Test",
            instrument_type="statute",
            date_of_version=None,
            uncertainty_notes="Unknown currency",
        )
        result = validate_instrument_metadata(m)
        assert not result.is_valid
        assert any(e.field == "jurisdiction" for e in result.errors)

    def test_missing_instrument_name(self):
        m = InstrumentMetadata(
            jurisdiction="CH",
            instrument_name="   ",  # blank
            instrument_type="federal statute",
            date_of_version="2013",
            is_current=True,
            completeness_verified=True,
            currency_verified=True,
        )
        result = validate_instrument_metadata(m)
        assert not result.is_valid
        assert any(e.field == "instrument_name" for e in result.errors)

    def test_missing_date_triggers_no_error_if_noted(self):
        """If is_current is None and uncertainty is documented, it should pass."""
        m = InstrumentMetadata(
            jurisdiction="MX",
            instrument_name="Test Law",
            instrument_type="statute",
            date_of_version=None,
            is_current=None,
            uncertainty_notes="Date of current version could not be verified; last confirmed version is 2018.",
        )
        result = validate_instrument_metadata(m)
        assert result.is_valid

    def test_unverified_currency_without_note_fails(self):
        """Unverified currency without uncertainty notes violates Rule 2."""
        m = InstrumentMetadata(
            jurisdiction="MX",
            instrument_name="Test Law",
            instrument_type="statute",
            date_of_version=None,
            is_current=None,
            uncertainty_notes="",  # no note
        )
        result = validate_instrument_metadata(m)
        assert not result.is_valid
        assert any(e.field == "uncertainty_notes" for e in result.errors)

    def test_invalid_date_format(self):
        m = InstrumentMetadata(
            jurisdiction="CH",
            instrument_name="ZGB",
            instrument_type="federal statute",
            date_of_version="13/04/2026",  # not ISO 8601
            is_current=True,
        )
        result = validate_instrument_metadata(m)
        assert not result.is_valid
        assert any(e.field == "date_of_version" for e in result.errors)

    def test_valid_iso_date_formats(self):
        for date_str in ("2011", "2011-06", "2011-06-01"):
            m = InstrumentMetadata(
                jurisdiction="MX",
                instrument_name="Test",
                instrument_type="statute",
                date_of_version=date_str,
                is_current=True,
                completeness_verified=True,
                currency_verified=True,
            )
            result = validate_instrument_metadata(m)
            assert result.is_valid, f"Expected valid for date '{date_str}'"

    def test_warns_on_unverified_completeness(self):
        m = InstrumentMetadata(
            jurisdiction="MX",
            instrument_name="Test Law",
            instrument_type="statute",
            date_of_version="2020",
            is_current=True,
            completeness_verified=False,  # trigger warning
            currency_verified=True,
        )
        result = validate_instrument_metadata(m)
        assert result.is_valid  # warning, not error
        assert any(e.field == "completeness_verified" for e in result.warnings)


class TestAssessObligationVerb:
    def test_strong_spanish(self):
        text = "El Estado garantizará el acceso a servicios de apoyo para personas con discapacidad."
        result = assess_obligation_verb(text)
        assert result["assessment"] == "strong"
        assert result["obligation_language_model"] == "justiciable"

    def test_weak_spanish(self):
        text = "El Estado promoverá la inclusión laboral de personas con discapacidad."
        result = assess_obligation_verb(text)
        assert result["assessment"] == "weak"
        assert result["obligation_language_model"] == "programmatic"

    def test_mixed_weakens_to_programmatic(self):
        text = "El Estado asegurará la accesibilidad, sujeto a disponibilidad presupuestal."
        result = assess_obligation_verb(text)
        assert result["assessment"] == "mixed"
        assert result["obligation_language_model"] == "programmatic"

    def test_strong_english(self):
        text = "The State shall ensure that all persons with disabilities have the right to access support services."
        result = assess_obligation_verb(text)
        assert result["assessment"] == "strong"

    def test_weak_english(self):
        text = "The State shall encourage inclusion of persons with disabilities to the extent possible."
        result = assess_obligation_verb(text)
        assert result["assessment"] == "weak" or result["assessment"] == "mixed"
        assert result["obligation_language_model"] == "programmatic"

    def test_indeterminate(self):
        text = "Disability services are provided by multiple actors at different levels."
        result = assess_obligation_verb(text)
        assert result["assessment"] == "indeterminate"


class TestAssessEnforceabilityMarkers:
    def test_rich_text_scores_high(self):
        text = """
        El organismo competente establecerá las sanciones correspondientes.
        Las personas con discapacidad podrán interponer un recurso ante la autoridad.
        El monitoreo de esta ley estará a cargo de la Comisión.
        Se asignará una partida presupuestal para su implementación.
        """
        result = assess_enforceability_markers(text)
        assert result["enforceability_score"] >= 3
        assert result["enforceability_level"] in ("medium", "high")

    def test_bare_text_scores_low(self):
        text = "Se promoverá la inclusión de las personas con discapacidad en todos los ámbitos de la vida."
        result = assess_enforceability_markers(text)
        assert result["enforceability_score"] <= 1
        assert result["enforceability_level"] == "low"

    def test_detects_budgetary_conditionality(self):
        text = "El Estado garantizará los servicios sujeto a disponibilidad presupuestal."
        result = assess_enforceability_markers(text)
        assert result["budgetary_conditionality"] is True

    def test_no_conditionality_when_absent(self):
        text = "El Estado garantizará plenamente el acceso a servicios de apoyo."
        result = assess_enforceability_markers(text)
        assert result["budgetary_conditionality"] is False


class TestValidateGapFinding:
    def _valid_finding(self) -> GapFinding:
        f = GapFinding(
            jurisdiction="MX",
            domestic_legal_instrument="Ley General para la Inclusión de las Personas con Discapacidad",
            legal_instrument_type="federal statute",
            gap_type=GapType.INCOMPATIBILITY,
            gap_severity=GapSeverity.CRITICAL,
            article_number=12,
            gap_description="No supported decision-making provision; guardianship persists.",
            evidence_excerpts=["Art. 38: Se declarará en estado de interdicción..."],
        )
        return f

    def test_valid_finding_passes(self):
        result = validate_gap_finding(self._valid_finding())
        assert result.is_valid

    def test_missing_jurisdiction_fails(self):
        f = self._valid_finding()
        f.jurisdiction = ""
        result = validate_gap_finding(f)
        assert not result.is_valid
        assert any(e.field == "jurisdiction" for e in result.errors)

    def test_missing_gap_type_fails(self):
        f = self._valid_finding()
        f.gap_type = None
        result = validate_gap_finding(f)
        assert not result.is_valid
        assert any(e.field == "gap_type" for e in result.errors)

    def test_critical_without_evidence_fails(self):
        f = self._valid_finding()
        f.evidence_excerpts = []
        result = validate_gap_finding(f)
        assert not result.is_valid
        assert any(e.field == "evidence_excerpts" for e in result.errors)

    def test_uncertain_without_notes_fails(self):
        f = self._valid_finding()
        f.gap_severity = GapSeverity.UNCERTAIN
        f.notes_on_uncertainty = ""
        result = validate_gap_finding(f)
        assert not result.is_valid
        assert any(e.field == "notes_on_uncertainty" for e in result.errors)

    def test_uncertain_with_notes_passes(self):
        f = self._valid_finding()
        f.gap_severity = GapSeverity.UNCERTAIN
        f.notes_on_uncertainty = "The 2024 amendment may have modified this provision; verification pending."
        result = validate_gap_finding(f)
        assert result.is_valid

    def test_missing_rights_holder_warns(self):
        f = self._valid_finding()
        f.rights_holder_group = ""
        result = validate_gap_finding(f)
        # Warning, not blocking error
        assert result.is_valid
        assert any(e.field == "rights_holder_group" for e in result.warnings)


class TestValidateFindingsBatch:
    def test_all_valid(self):
        findings = [
            GapFinding(
                jurisdiction="MX",
                domestic_legal_instrument="Test Law",
                gap_type=GapType.TOTAL_ABSENCE,
                gap_severity=GapSeverity.HIGH,
                article_number=9,
                evidence_excerpts=["No accessibility provision found."],
            )
            for _ in range(3)
        ]
        report = validate_findings_batch(findings)
        assert report["all_valid"]
        assert report["valid"] == 3

    def test_mixed_validity(self):
        valid = GapFinding(
            jurisdiction="MX",
            domestic_legal_instrument="Test Law",
            gap_type=GapType.TOTAL_ABSENCE,
            gap_severity=GapSeverity.HIGH,
            article_number=9,
            evidence_excerpts=["No provision found."],
        )
        invalid = GapFinding(jurisdiction="")  # missing fields
        report = validate_findings_batch([valid, invalid])
        assert not report["all_valid"]
        assert report["valid"] == 1
        assert report["invalid"] == 1
