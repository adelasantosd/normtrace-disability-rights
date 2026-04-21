"""
NormTrace
=========
Multilevel normative analysis tool for assessing domestic legal alignment
with international human rights instruments.

NormTrace is designed as scientific software: the analytical framework —
gap taxonomy, CRPD standards, analytical criteria, reference corpus — exists
as structured Python objects and data files, independently of any language
model. The LLM is an extraction component that populates these structures;
the structures themselves define what the analysis is.

Architecture
------------
- ``normtrace.models`` — core dataclasses (all enums, all analytical types)
- ``normtrace.standards`` — CRPD articles and General Comments as objects
- ``normtrace.taxonomy`` — gap taxonomy with classification and scoring logic
- ``normtrace.criteria`` — analytical criteria as structured rule objects
- ``normtrace.validators`` — pure validation functions (Stage 0 and output)
- ``normtrace.references`` — reference corpus with citation generation

Data
----
- ``data/crpd/`` — CRPD articles, General Comments (JSON)
- ``data/frameworks/`` — gap taxonomy, gender criteria, intersectionality axes (JSON)
- ``data/references/`` — jurisprudence, doctrine (JSON)

Citation
--------
Santos-Domínguez, A. B. (2026). NormTrace (v2.0.0).
Zenodo. https://doi.org/10.5281/zenodo.19452837
"""

__version__ = "2.1.0"
__author__ = "Adela B. Santos-Domínguez"
__license__ = "MIT"
__doi__ = "10.5281/zenodo.19452837"

from normtrace.models import (
    AnalyticalCriterion,
    AnalyticalStage,
    BindingForce,
    CRPDArticle,
    CRPDPrinciple,
    CriterionResult,
    DoctrinalReference,
    GapFinding,
    GapSeverity,
    GapType,
    GeneralComment,
    InstrumentMetadata,
    IntersectionalityAxis,
    JurisdictionType,
    LegalReference,
    MinimumStandard,
    ObligationType,
    RedFlag,
    ReferenceType,
)

__all__ = [
    "__version__",
    "__doi__",
    # Models
    "AnalyticalCriterion",
    "AnalyticalStage",
    "BindingForce",
    "CRPDArticle",
    "CRPDPrinciple",
    "CriterionResult",
    "DoctrinalReference",
    "GapFinding",
    "GapSeverity",
    "GapType",
    "GeneralComment",
    "InstrumentMetadata",
    "IntersectionalityAxis",
    "JurisdictionType",
    "LegalReference",
    "MinimumStandard",
    "ObligationType",
    "RedFlag",
    "ReferenceType",
]
