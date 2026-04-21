"""
normtrace.models
================
Core data structures for the NormTrace analytical framework.

These classes represent the analytical vocabulary of NormTrace as typed,
instantiable Python objects. They are independent of any language model:
the LLM is a downstream extraction component that populates these structures;
the structures themselves define what the analysis is.

Design principles
-----------------
- Pure dataclasses: no I/O, no external dependencies, fully serialisable.
- Enumerations for all controlled vocabularies, preventing free-text drift.
- Every field that encodes a normative claim carries a ``source`` reference
  traceable to a specific treaty provision, General Comment, or case law entry.

References
----------
Convention on the Rights of Persons with Disabilities (CRPD), G.A. Res.
61/106, U.N. Doc. A/RES/61/106 (Dec. 13, 2006), entered into force May 3, 2008.

CRPD Committee, General Comments No. 1–7 (2014–2022).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Controlled vocabularies (Enums)
# ---------------------------------------------------------------------------


class ObligationType(str, Enum):
    """Tripartite typology of state obligations under international human rights law.

    Source: Committee on Economic, Social and Cultural Rights, General Comment
    No. 12 (1999), para. 15; elaborated across CRPD Committee General Comments.
    """
    RESPECT = "respect"
    """Negative obligation: refrain from interfering with the enjoyment of a right."""
    PROTECT = "protect"
    """Positive obligation: prevent third parties from interfering with a right."""
    FULFIL = "fulfil"
    """Positive obligation: take measures to realise a right progressively."""


class GapType(str, Enum):
    """Taxonomy of normative gaps between international standard and domestic law.

    Source: NormTrace analytical protocol, Stage 3 (conventionality analysis);
    draws on CRPD Committee methodology in concluding observations to Mexico
    (CRPD/C/MEX/CO/1, 2014) and Switzerland (CRPD/C/CHE/CO/1, 2022).
    """
    TOTAL_ABSENCE = "total_absence"
    """The right, obligation, or institutional mechanism is entirely absent from
    the domestic instrument."""
    WEAK_RECOGNITION = "weak_recognition"
    """The right is mentioned but without enforceable content, implementation
    pathway, or monitoring mechanism."""
    INCOMPATIBILITY = "incompatibility"
    """A domestic provision actively contradicts the international standard
    (e.g., substituted decision-making vs. CRPD Art. 12)."""
    REGRESSION = "regression"
    """A previous domestic standard gave greater protection; the current
    instrument reduces it."""
    STRUCTURAL_DISCRIMINATION = "structural_discrimination"
    """A facially neutral provision produces discriminatory effects for a
    protected group (indirect discrimination), or embeds historical inequality."""
    IMPLEMENTATION_GAP = "implementation_gap"
    """The right is formally recognised but institutional design, budgetary
    pathway, or enforcement mechanism is insufficient for realisation."""
    NORMATIVE_SILENCE = "normative_silence"
    """An absence that is analytically meaningful: the law regulates a domain
    without addressing a dimension that international standards require."""
    DECLARATORY_ONLY = "declaratory_only"
    """Rights language is present but the instrument does not generate
    justiciable obligations (programmatic or aspirational framing only)."""


class GapSeverity(str, Enum):
    """Ordinal severity scale for gap classification.

    Severity is determined by a combination of: rights-holder exposure,
    reversibility, systemic scope, and availability of domestic remedies.
    See normtrace.scoring for the quantitative scoring function.
    """
    CRITICAL = "critical"
    """Directly enables or perpetuates a human rights violation; highest
    priority for litigation or legislative reform."""
    HIGH = "high"
    """Significantly impairs rights enjoyment; remediation is urgent."""
    MEDIUM = "medium"
    """Partial compliance; impairs but does not negate rights enjoyment."""
    LOW = "low"
    """Minor deviation; domestic framework substantially compliant."""
    UNCERTAIN = "uncertain"
    """Insufficient information to assess severity; uncertainty must be
    flagged explicitly in the analytical output."""


class IntersectionalityAxis(str, Enum):
    """Axes of intersectional analysis applied in Stage 2 (exclusion analysis).

    Source: NormTrace exclusion-analysis framework; draws on Crenshaw, K.
    (1989) 'Demarginalising the intersection of race and sex', University of
    Chicago Legal Forum, 139–167; and CRPD Committee GC No. 3 (2016) on
    women and girls with disabilities.
    """
    GENDER = "gender"
    ETHNICITY_INDIGENEITY = "ethnicity_indigeneity"
    AGE = "age"
    CLASS_POVERTY = "class_poverty"
    RURALITY = "rurality"
    MIGRATION_STATUS = "migration_status"
    SEXUAL_ORIENTATION_GENDER_IDENTITY = "sexual_orientation_gender_identity"
    DEPRIVATION_OF_LIBERTY = "deprivation_of_liberty"


class AnalyticalStage(str, Enum):
    """The five analytical stages of the NormTrace protocol."""
    INGESTION = "stage_0_ingestion"
    STRUCTURAL = "stage_1_structural"
    EXCLUSION = "stage_2_exclusion"
    CONVENTIONALITY = "stage_3_conventionality"
    ARGUMENTATION = "stage_4_argumentation"


class JurisdictionType(str, Enum):
    """Type of legal system for jurisdiction-sensitive framing.

    Source: NormTrace conventionality-analysis framework.
    """
    CONVENTIONALITY_CONTROL = "conventionality_control"
    """Mexico and other Latin American systems where domestic courts exercise
    ex officio conventionality review. Source: IACtHR, Almonacid Arellano et al.
    v. Chile, Series C No. 154 (2006), para. 124."""
    INTERNATIONAL_COMPATIBILITY_ANALYSIS = "international_compatibility_analysis"
    """Switzerland and monist systems where international law is directly
    incorporated but subject to direct-applicability assessment and limited
    constitutional review of federal statutes."""
    DUALIST_INCORPORATION = "dualist_incorporation"
    """Systems requiring domestic implementing legislation before treaty
    provisions become enforceable."""


class ReferenceType(str, Enum):
    """Type of legal reference in the normtrace reference corpus."""
    TREATY = "treaty"
    GENERAL_COMMENT = "general_comment"
    CONCLUDING_OBSERVATIONS = "concluding_observations"
    JURISPRUDENCE_NATIONAL = "jurisprudence_national"
    JURISPRUDENCE_INTERNATIONAL = "jurisprudence_international"
    DOCTRINE = "doctrine"
    SOFT_LAW = "soft_law"


class BindingForce(str, Enum):
    """Binding force of a legal reference in international and domestic law."""
    BINDING_TREATY = "binding_treaty"
    AUTHORITATIVE_INTERPRETATION = "authoritative_interpretation"
    """General Comments: authoritative but not formally binding."""
    PERSUASIVE = "persuasive"
    """Concluding observations, Special Procedure reports, doctrine."""
    BINDING_DOMESTIC = "binding_domestic"
    """Domestic constitutional or statutory norm."""


# ---------------------------------------------------------------------------
# Core analytical structures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CRPDPrinciple:
    """One of the eight general principles of the CRPD (Article 3).

    Source: CRPD, Art. 3(a)–(h).
    """
    label: str
    """Short identifier, e.g. 'dignity', 'autonomy', 'accessibility'."""
    text: str
    """Verbatim or near-verbatim text from Art. 3."""
    article_subparagraph: str
    """Subparagraph reference, e.g. 'Art. 3(a)'."""


@dataclass(frozen=True)
class MinimumStandard:
    """Minimum content of a right under a CRPD article.

    'Minimum core obligations' in the sense elaborated by the CESCR and
    applied in CRPD Committee practice: the floor below which a state cannot
    fall without violating the treaty.
    """
    description: str
    """Substantive content of the minimum standard."""
    source_article: int
    """CRPD article number."""
    source_paragraphs: list[str] = field(default_factory=list)
    """Specific paragraphs of the article or General Comment."""
    general_comment_ids: list[str] = field(default_factory=list)
    """GC identifiers, e.g. ['GC_1', 'GC_2'] for GC No. 1 and No. 2."""


@dataclass(frozen=True)
class RedFlag:
    """A legislative pattern that presumptively indicates non-compliance.

    Red flags are not conclusive; they trigger deeper analysis. They are
    derived inductively from CRPD Committee concluding observations and
    the NormTrace analytical protocol.
    """
    pattern: str
    """Description of the legislative pattern (e.g., 'substituted decision-making')."""
    gap_type: GapType
    """The gap type this pattern most commonly signals."""
    severity_presumption: GapSeverity
    """Presumptive severity pending full analysis."""
    relevant_article: int
    """Primary CRPD article engaged."""
    rationale: str = ""
    """Why this pattern is a red flag."""


@dataclass(frozen=True)
class CRPDArticle:
    """Structured representation of a CRPD article as an analytical object.

    This is not a text container — it is the article as a machine-readable
    normative specification. The LLM receives instances of this class as
    the standard against which it extracts gap findings.
    """
    number: int
    """Article number (1–50)."""
    title: str
    """Article title as in the official UN text."""
    obligation_types: list[ObligationType]
    """Primary obligation types generated by this article."""
    minimum_standards: list[MinimumStandard]
    """Minimum core obligations under this article."""
    red_flags: list[RedFlag]
    """Legislative patterns indicating probable non-compliance."""
    interpretive_authority: list[str] = field(default_factory=list)
    """General Comments and other authoritative interpretations, by ID."""
    cross_cutting: bool = False
    """True for articles that generate cross-cutting obligations
    (e.g., Art. 3 principles, Art. 4 general obligations, Art. 9 accessibility)."""
    notes: str = ""


@dataclass(frozen=True)
class GeneralComment:
    """A CRPD Committee General Comment as a structured analytical object.

    General Comments are authoritative (though not formally binding) interpretations
    of treaty obligations. They are key inputs to the conventionality analysis stage.

    Source: CRPD Committee, Rules of Procedure, Rule 47.
    """
    id: str
    """Identifier, e.g. 'GC_1' for General Comment No. 1."""
    number: int
    article_addressed: int
    """Primary CRPD article interpreted."""
    title: str
    year: int
    document_symbol: str
    """UN document symbol, e.g. 'CRPD/C/GC/1'."""
    key_holdings: list[str]
    """Core interpretive pronouncements, in summary form."""
    binding_force: BindingForce = BindingForce.AUTHORITATIVE_INTERPRETATION
    url: str = "https://www.ohchr.org/en/treaty-bodies/crpd/general-comments"


# ---------------------------------------------------------------------------
# Analytical criterion structures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AnalyticalCriterion:
    """A single diagnostic criterion within an analytical stage.

    Criteria are the unit of analysis: each criterion is a question the
    analyst (or LLM) applies to the domestic instrument. The answer is
    always structured — never free-form — enabling coding for comparative work.
    """
    id: str
    """Unique identifier, e.g. 'gender_01', 'struct_enforceability_01'."""
    stage: AnalyticalStage
    dimension: str
    """Sub-dimension within the stage, e.g. 'gender_perspective', 'structural'."""
    question: str
    """The diagnostic question posed to the text."""
    positive_indicators: list[str]
    """Text patterns or legislative features that satisfy this criterion."""
    negative_indicators: list[str]
    """Red flags: text patterns or absences that indicate non-satisfaction."""
    applicable_articles: list[int] = field(default_factory=list)
    """CRPD articles this criterion primarily engages."""
    weight: float = 1.0
    """Relative weight in aggregate scoring (1.0 = baseline)."""
    rationale: str = ""
    """Why this criterion matters; sourced to treaty provision or GC."""


@dataclass
class CriterionResult:
    """The result of applying a single AnalyticalCriterion to a domestic text.

    This is the atomic output of LLM-assisted extraction: the LLM reads the
    domestic instrument and returns a CriterionResult for each criterion.
    Downstream scoring and classification use only these structured results.
    """
    criterion_id: str
    satisfied: Optional[bool]
    """True = satisfied; False = not satisfied; None = insufficient information."""
    evidence_excerpt: str = ""
    """Quoted passage from the domestic instrument supporting the result."""
    confidence: float = 1.0
    """Extraction confidence (0–1). Low confidence triggers uncertainty flag."""
    notes: str = ""


# ---------------------------------------------------------------------------
# Gap finding structures
# ---------------------------------------------------------------------------


@dataclass
class GapFinding:
    """A structured finding of non-alignment between a domestic norm and
    an international standard.

    GapFindings are the primary output of the NormTrace analysis. They are
    designed to be directly codeable for comparative/quantitative work.

    Coding fields correspond to those specified in the NormTrace protocol,
    §'Coding-ready analytical summaries'.
    """
    # Instrument metadata
    jurisdiction: str
    """ISO 3166-1 alpha-2 country code, e.g. 'MX', 'CH'."""
    subnational_level: Optional[str] = None
    """Canton, state, or municipality, if applicable."""
    domestic_legal_instrument: str = ""
    """Full name of the domestic instrument analysed."""
    legal_instrument_type: str = ""
    """E.g. 'federal statute', 'cantonal ordinance', 'constitutional provision'."""
    date_of_version_analysed: Optional[str] = None
    """ISO 8601 date of the version analysed, or None if uncertain."""

    # International standard engaged
    international_instrument: str = "CRPD"
    article_number: Optional[int] = None
    standard_description: str = ""

    # Gap characterisation
    gap_type: Optional[GapType] = None
    gap_severity: Optional[GapSeverity] = None
    gap_description: str = ""
    """Free-text description for human review; structured fields are for coding."""

    # Rights-holder and actor dimensions
    rights_holder_group: str = ""
    """Primary affected group, e.g. 'persons with disabilities'."""
    subgroup_affected: list[str] = field(default_factory=list)
    """Specific subgroups (intersectional), e.g. ['women', 'indigenous peoples']."""
    actor_responsible: str = ""
    """State or institutional actor bearing the obligation."""
    private_actor_included: bool = False

    # Structural indicators
    enforceability_level: str = ""
    """'justiciable', 'programmatic', 'declaratory', 'absent'."""
    budgetary_pathway_present: Optional[bool] = None
    monitoring_mechanism_present: Optional[bool] = None
    participation_mechanism_present: Optional[bool] = None

    # Intersectional/cross-cutting dimensions
    gender_dimension_present: Optional[bool] = None
    intersectional_dimension_present: Optional[bool] = None
    cultural_or_linguistic_dimension_present: Optional[bool] = None

    # Normative language model
    language_model: str = ""
    """'rights-based', 'assistentialist', 'mixed'."""
    overall_normative_alignment: str = ""
    """'aligned', 'partially_aligned', 'non_aligned', 'regressive'."""

    # Epistemic markers
    notes_on_uncertainty: str = ""
    evidence_excerpts: list[str] = field(default_factory=list)
    criterion_results: list[CriterionResult] = field(default_factory=list)


@dataclass(frozen=True)
class InstrumentMetadata:
    """Metadata required for ingestion and verification of a domestic legal instrument.

    Corresponds to Stage 0 (Text Ingestion & Verification) of the protocol.
    Verification of these fields is a pre-condition for proceeding with analysis.
    """
    jurisdiction: str
    """ISO 3166-1 alpha-2 code."""
    instrument_name: str
    instrument_type: str
    date_of_version: Optional[str]
    """ISO 8601. If unknown, must be None — not inferred."""
    source_url: str = ""
    is_current: Optional[bool] = None
    """None until verified; never assumed True."""
    completeness_verified: bool = False
    currency_verified: bool = False
    uncertainty_notes: str = ""
    """Mandatory field: any doubts about the instrument must be recorded here."""


# ---------------------------------------------------------------------------
# Reference structures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LegalReference:
    """A structured bibliographic reference in the NormTrace corpus.

    All interpretive claims in NormTrace outputs must be traceable to a
    LegalReference in the corpus. This ensures reproducibility and allows
    automated citation generation.
    """
    id: str
    """Unique identifier, e.g. 'IACtHR_Almonacid_2006'."""
    reference_type: ReferenceType
    title: str
    year: int
    binding_force: BindingForce

    # Optional fields vary by reference type
    court_or_body: str = ""
    """E.g. 'CRPD Committee', 'SCJN', 'IACtHR', 'Federal Supreme Court (CH)'."""
    document_symbol: str = ""
    """E.g. 'CRPD/C/MEX/CO/1', 'Amparo en Revisión 410/2012'."""
    jurisdiction: str = ""
    """ISO 3166-1 alpha-2 or 'INT' for international."""
    url: str = ""
    key_holdings: list[str] = field(default_factory=list)
    relevant_articles: list[int] = field(default_factory=list)
    """CRPD articles engaged."""
    notes: str = ""


@dataclass(frozen=True)
class DoctrinalReference:
    """An academic doctrinal reference supporting a normative claim."""
    id: str
    authors: list[str]
    title: str
    year: int
    publication: str
    """Journal, book, or report title."""
    pages: str = ""
    doi: str = ""
    url: str = ""
    relevance: str = ""
    """One-sentence description of relevance to NormTrace methodology."""
