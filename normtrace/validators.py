"""
normtrace.validators
====================
Pure validation functions for NormTrace analytical inputs and outputs.

All functions in this module are stateless and have no side effects. They
operate on structured data (dataclasses, dicts) and return either
structured results or raise ``ValueError`` with informative messages.

Validation in NormTrace serves two roles:
1. **Input validation**: ensuring domestic instrument metadata is complete
   and honest about uncertainty before analysis begins (Stage 0).
2. **Output validation**: checking that GapFindings are fully coded and
   epistemically consistent (uncertainty flags, evidence requirements).

References
----------
Stage 0 (ingestion) and non-negotiable analytical rules: NormTrace
analytical protocol v2.0; Rule 2 (do not assume currency), Rule 9
(state uncertainty explicitly), Rule 10 (acknowledge incomplete texts).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from normtrace.models import (
    GapFinding,
    GapSeverity,
    GapType,
    InstrumentMetadata,
)

# ---------------------------------------------------------------------------
# Validation result types
# ---------------------------------------------------------------------------


@dataclass
class ValidationError:
    """A single validation error with field name and message."""
    field: str
    message: str
    is_blocking: bool = True
    """Blocking errors prevent analysis from proceeding; non-blocking are warnings."""


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    errors: list[ValidationError]
    warnings: list[ValidationError]

    @property
    def blocking_errors(self) -> list[ValidationError]:
        return [e for e in self.errors if e.is_blocking]

    def summary(self) -> str:
        parts = [f"{'VALID' if self.is_valid else 'INVALID'}"]
        if self.errors:
            parts.append(f"{len(self.errors)} error(s)")
        if self.warnings:
            parts.append(f"{len(self.warnings)} warning(s)")
        return ", ".join(parts)


# ---------------------------------------------------------------------------
# Instrument metadata validation (Stage 0)
# ---------------------------------------------------------------------------


def validate_instrument_metadata(metadata: InstrumentMetadata) -> ValidationResult:
    """Validate instrument metadata for Stage 0 ingestion.

    Enforces the non-negotiable rules:
    - Do not assume a law is current if version/date is uncertain (Rule 2).
    - State uncertainty explicitly (Rule 9).
    - Acknowledge incomplete or unverified texts (Rule 10).

    Parameters
    ----------
    metadata:
        ``InstrumentMetadata`` instance to validate.

    Returns
    -------
    ValidationResult
    """
    errors: list[ValidationError] = []
    warnings: list[ValidationError] = []

    # Jurisdiction must be ISO 3166-1 alpha-2
    if not metadata.jurisdiction or not re.match(r"^[A-Z]{2}$", metadata.jurisdiction):
        errors.append(
            ValidationError(
                field="jurisdiction",
                message=(
                    f"Jurisdiction '{metadata.jurisdiction}' is not a valid "
                    "ISO 3166-1 alpha-2 code (e.g., 'MX', 'CH')."
                ),
            )
        )

    # Instrument name must be present
    if not metadata.instrument_name.strip():
        errors.append(
            ValidationError(
                field="instrument_name",
                message="Instrument name is required; cannot be empty.",
            )
        )

    # Instrument type must be present
    if not metadata.instrument_type.strip():
        errors.append(
            ValidationError(
                field="instrument_type",
                message=(
                    "Instrument type is required (e.g., 'federal statute', "
                    "'cantonal ordinance', 'constitutional provision')."
                ),
            )
        )

    # Date of version: if present, must be ISO 8601 (YYYY, YYYY-MM, or YYYY-MM-DD)
    if metadata.date_of_version is not None:
        if not re.match(r"^\d{4}(-\d{2}(-\d{2})?)?$", metadata.date_of_version):
            errors.append(
                ValidationError(
                    field="date_of_version",
                    message=(
                        f"Date '{metadata.date_of_version}' must be in ISO 8601 format "
                        "(YYYY, YYYY-MM, or YYYY-MM-DD). If unknown, set to None."
                    ),
                )
            )

    # Currency and completeness must be verified or uncertainty explicitly noted
    if metadata.is_current is None and not metadata.uncertainty_notes.strip():
        errors.append(
            ValidationError(
                field="uncertainty_notes",
                message=(
                    "Currency of the instrument is unverified (is_current=None) "
                    "but no uncertainty_notes are provided. "
                    "Per Rule 2: do not assume currency. Document uncertainty explicitly."
                ),
            )
        )

    if not metadata.completeness_verified:
        warnings.append(
            ValidationError(
                field="completeness_verified",
                message=(
                    "Completeness of the instrument has not been verified. "
                    "Ensure the full text (not a summary or excerpt) has been ingested "
                    "before proceeding with analysis."
                ),
                is_blocking=False,
            )
        )

    if not metadata.currency_verified:
        warnings.append(
            ValidationError(
                field="currency_verified",
                message=(
                    "Currency of the instrument has not been verified. "
                    "Check for amendments, reforms, or repeals before proceeding."
                ),
                is_blocking=False,
            )
        )

    is_valid = len([e for e in errors if e.is_blocking]) == 0
    return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)


# ---------------------------------------------------------------------------
# Obligation verb assessment (pure linguistic heuristic)
# ---------------------------------------------------------------------------

# Verbs indicating strong (justiciable) obligations
STRONG_OBLIGATION_VERBS: frozenset[str] = frozenset(
    {
        # Spanish
        "garantizará", "garantizar", "garantiza", "garanticen",
        "asegurará", "asegurar", "asegura",
        "reconoce", "reconocerá", "reconocer",
        "prohíbe", "prohibirá", "prohibir",
        "tiene derecho", "tendrán derecho",
        "deberá", "deberán", "debe", "deben",
        # German
        "gewährleistet", "gewährleisten", "sicherstellt", "sicherstellen",
        "garantiert", "garantieren", "hat Anspruch", "haben Anspruch",
        "ist verpflichtet", "sind verpflichtet",
        # French
        "garantit", "garantissent", "assure", "assurent",
        "a droit", "ont droit", "est tenu", "sont tenus",
        # English
        "shall ensure", "shall guarantee", "shall prohibit",
        "has the right", "have the right",
        "must", "is obliged", "are obliged",
    }
)

# Verbs indicating weak (programmatic/declaratory) obligations
WEAK_OBLIGATION_VERBS: frozenset[str] = frozenset(
    {
        # Spanish
        "promoverá", "promover", "promueve",
        "fomentará", "fomentar", "fomenta",
        "impulsará", "impulsar", "impulsa",
        "procurará", "procurar", "procura",
        "buscará", "buscar", "busca",
        "en la medida de", "de conformidad con",
        "sujeto a disponibilidad presupuestal",
        "según sus posibilidades presupuestales",
        # German
        "fördert", "fördern", "strebt an", "soll",
        "im Rahmen der verfügbaren Mittel",
        # French
        "encourage", "favorise", "s'efforce", "dans la mesure de ses moyens",
        "en fonction des ressources disponibles",
        # English
        "shall promote", "shall encourage", "shall endeavour",
        "subject to available resources", "to the extent possible",
        "where appropriate", "as appropriate",
    }
)


def assess_obligation_verb(text_fragment: str) -> dict:
    """Heuristically assess whether a text fragment contains strong or weak obligation language.

    This is a structural heuristic, not a full parsing solution. It flags
    the presence of known strong or weak obligation verb patterns.

    Parameters
    ----------
    text_fragment:
        A sentence or paragraph from a domestic legal instrument.

    Returns
    -------
    dict with keys:
        - 'strong_matches': list of strong obligation verbs found
        - 'weak_matches': list of weak obligation verbs found
        - 'assessment': 'strong', 'weak', 'mixed', or 'indeterminate'
        - 'obligation_language_model': 'justiciable', 'programmatic', or 'indeterminate'
    """
    text_lower = text_fragment.lower()
    strong = [v for v in STRONG_OBLIGATION_VERBS if v in text_lower]
    weak = [v for v in WEAK_OBLIGATION_VERBS if v in text_lower]

    if strong and not weak:
        assessment = "strong"
        language_model = "justiciable"
    elif weak and not strong:
        assessment = "weak"
        language_model = "programmatic"
    elif strong and weak:
        assessment = "mixed"
        language_model = "programmatic"  # weak overrides: if any weakener present, obligation is weakened
    else:
        assessment = "indeterminate"
        language_model = "indeterminate"

    return {
        "strong_matches": strong,
        "weak_matches": weak,
        "assessment": assessment,
        "obligation_language_model": language_model,
    }


# ---------------------------------------------------------------------------
# Enforceability marker assessment
# ---------------------------------------------------------------------------

ENFORCEABILITY_MARKERS: dict[str, list[str]] = {
    "sanction_present": [
        "sanción", "sanción administrativa", "multa", "infracción",
        "Busse", "Strafe", "Sanktion",
        "amende", "sanction", "infraction",
        "fine", "penalty", "sanction",
    ],
    "remedy_present": [
        "recurso", "recurso de amparo", "acción legal", "tutela judicial",
        "Rechtsmittel", "Beschwerde", "Klage",
        "recours", "voie de recours",
        "remedy", "appeal", "complaint", "judicial review",
    ],
    "monitoring_present": [
        "monitoreo", "seguimiento", "evaluación", "informe",
        "Monitoring", "Berichterstattung", "Überwachung",
        "suivi", "évaluation", "rapport",
        "monitoring", "reporting", "review", "evaluation",
    ],
    "institutional_anchor": [
        "organismo", "institución", "comisión", "secretaría", "ministerio",
        "Behörde", "Amt", "Kommission", "Ministerium",
        "organisme", "commission", "ministère",
        "body", "authority", "commission", "ministry", "department",
    ],
    "budgetary_pathway": [
        "partida presupuestal", "asignación", "presupuesto",
        "Haushaltsmittel", "Kredit", "Budget",
        "crédit budgétaire", "financement",
        "appropriation", "budget", "funding", "allocation",
    ],
}

BUDGETARY_CONDITIONALITY_MARKERS: list[str] = [
    "sujeto a disponibilidad presupuestal",
    "de conformidad con el presupuesto",
    "según las posibilidades presupuestales",
    "im Rahmen der verfügbaren Mittel",
    "vorbehaltlich der Mittel",
    "dans la mesure des ressources disponibles",
    "subject to available resources",
    "within available resources",
    "to the extent of available resources",
]


def assess_enforceability_markers(text: str) -> dict:
    """Assess the presence of enforceability markers in a domestic legal text.

    Enforceability markers are structural features that determine whether a
    right recognised in law is actually justiciable and realisable. Their
    absence is a primary indicator of an implementation gap.

    Parameters
    ----------
    text:
        The full text of a domestic instrument section or chapter.

    Returns
    -------
    dict with keys:
        - 'markers_found': dict mapping marker type to list of matched strings
        - 'markers_absent': list of marker types not found
        - 'budgetary_conditionality': bool — True if conditionality language found
        - 'enforceability_score': int (0–5), one point per marker type found
        - 'enforceability_level': 'high' (4–5), 'medium' (2–3), 'low' (0–1)
    """
    text_lower = text.lower()
    found: dict[str, list[str]] = {}
    absent: list[str] = []

    for marker_type, patterns in ENFORCEABILITY_MARKERS.items():
        matches = [p for p in patterns if p in text_lower]
        if matches:
            found[marker_type] = matches
        else:
            absent.append(marker_type)

    budgetary_cond = any(m in text_lower for m in BUDGETARY_CONDITIONALITY_MARKERS)
    score = len(found)

    if score >= 4:
        level = "high"
    elif score >= 2:
        level = "medium"
    else:
        level = "low"

    return {
        "markers_found": found,
        "markers_absent": absent,
        "budgetary_conditionality": budgetary_cond,
        "enforceability_score": score,
        "enforceability_level": level,
    }


# ---------------------------------------------------------------------------
# GapFinding completeness validation
# ---------------------------------------------------------------------------


def validate_gap_finding(finding: GapFinding) -> ValidationResult:
    """Validate that a GapFinding is complete and epistemically consistent.

    A finding is complete if all coding fields required for comparative
    analysis are populated. A finding is epistemically consistent if
    uncertainty is flagged wherever confidence is low.

    Parameters
    ----------
    finding:
        A ``GapFinding`` instance to validate.

    Returns
    -------
    ValidationResult
    """
    errors: list[ValidationError] = []
    warnings: list[ValidationError] = []

    # Required fields
    if not finding.jurisdiction:
        errors.append(
            ValidationError("jurisdiction", "Jurisdiction code is required.")
        )
    if not finding.domestic_legal_instrument.strip():
        errors.append(
            ValidationError("domestic_legal_instrument", "Instrument name is required.")
        )
    if finding.gap_type is None:
        errors.append(
            ValidationError("gap_type", "Gap type must be classified.")
        )
    if finding.gap_severity is None:
        errors.append(
            ValidationError("gap_severity", "Gap severity must be assessed.")
        )
    if finding.article_number is None:
        errors.append(
            ValidationError("article_number", "CRPD article number must be specified.")
        )

    # Epistemic consistency: CRITICAL severity requires evidence
    if finding.gap_severity == GapSeverity.CRITICAL and not finding.evidence_excerpts:
        errors.append(
            ValidationError(
                "evidence_excerpts",
                "CRITICAL severity finding must include at least one evidence excerpt "
                "from the domestic instrument (or explicit documentation of absence).",
            )
        )

    # Uncertainty flag check
    if finding.gap_severity == GapSeverity.UNCERTAIN and not finding.notes_on_uncertainty.strip():
        errors.append(
            ValidationError(
                "notes_on_uncertainty",
                "UNCERTAIN severity requires explicit notes on what information is missing "
                "and why severity cannot be assessed (Rule 9: state uncertainty explicitly).",
            )
        )

    # Warnings for incomplete but non-blocking fields
    if not finding.rights_holder_group.strip():
        warnings.append(
            ValidationError(
                "rights_holder_group",
                "Rights-holder group not specified; required for comparative coding.",
                is_blocking=False,
            )
        )
    if not finding.language_model.strip():
        warnings.append(
            ValidationError(
                "language_model",
                "Language model ('rights-based', 'assistentialist', 'mixed') not specified.",
                is_blocking=False,
            )
        )
    if finding.gender_dimension_present is None:
        warnings.append(
            ValidationError(
                "gender_dimension_present",
                "Gender dimension assessment is None (not assessed); "
                "complete for full coding compliance.",
                is_blocking=False,
            )
        )

    is_valid = len([e for e in errors if e.is_blocking]) == 0
    return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)


def validate_findings_batch(findings: list[GapFinding]) -> dict:
    """Validate a batch of GapFindings and return a summary report.

    Parameters
    ----------
    findings:
        List of ``GapFinding`` instances.

    Returns
    -------
    dict with keys:
        - 'total': int
        - 'valid': int
        - 'invalid': int
        - 'results': list of ValidationResult
        - 'all_valid': bool
    """
    results = [validate_gap_finding(f) for f in findings]
    valid_count = sum(1 for r in results if r.is_valid)
    return {
        "total": len(findings),
        "valid": valid_count,
        "invalid": len(findings) - valid_count,
        "results": results,
        "all_valid": valid_count == len(findings),
    }
