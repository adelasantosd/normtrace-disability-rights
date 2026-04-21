"""
Tests for normtrace.references
================================
Verify that the reference corpus loads correctly and that citation
generation functions work for all reference types and styles.
"""

import pytest
from normtrace.models import BindingForce, ReferenceType
from normtrace.references import (
    DOCTRINE,
    JURISPRUDENCE,
    binding_references,
    concluding_observations_for_jurisdiction,
    doctrine_for_domain,
    generate_citation,
    get_doctrinal_reference,
    get_legal_reference,
    references_for_article,
    references_for_jurisdiction,
)


class TestCorpusLoads:
    def test_jurisprudence_not_empty(self):
        assert len(JURISPRUDENCE) > 0

    def test_doctrine_not_empty(self):
        assert len(DOCTRINE) > 0

    def test_almonacid_present(self):
        ref = get_legal_reference("IACtHR_Almonacid_2006")
        assert ref.year == 2006
        assert ref.jurisdiction == "INT"

    def test_scjn_cdt_293_present(self):
        ref = get_legal_reference("SCJN_CdT_293_2011")
        assert ref.jurisdiction == "MX"
        assert ref.binding_force == BindingForce.BINDING_DOMESTIC

    def test_crpd_co_mex_present(self):
        ref = get_legal_reference("CRPD_CO_MEX_2014")
        assert ref.reference_type == ReferenceType.CONCLUDING_OBSERVATIONS
        assert ref.binding_force == BindingForce.PERSUASIVE

    def test_crenshaw_present(self):
        ref = get_doctrinal_reference("Crenshaw_1989")
        assert "Crenshaw" in ref.authors[0]
        assert ref.year == 1989


class TestLookupFunctions:
    def test_unknown_legal_ref_raises(self):
        with pytest.raises(KeyError):
            get_legal_reference("MADE_UP_CASE_9999")

    def test_unknown_doctrinal_raises(self):
        with pytest.raises(KeyError):
            get_doctrinal_reference("MADE_UP_AUTHOR_9999")

    def test_references_for_article_12(self):
        refs = references_for_article(12)
        ref_ids = {r.id for r in refs}
        assert "SCJN_ADR_1387_2012" in ref_ids

    def test_references_for_jurisdiction_mx(self):
        refs = references_for_jurisdiction("MX")
        jurisdictions = {r.jurisdiction for r in refs}
        assert "MX" in jurisdictions or "INT" in jurisdictions

    def test_concluding_observations_mexico(self):
        obs = concluding_observations_for_jurisdiction("MX")
        assert len(obs) >= 1
        assert all(r.reference_type == ReferenceType.CONCLUDING_OBSERVATIONS for r in obs)
        assert any("MEX" in r.document_symbol for r in obs)

    def test_concluding_observations_switzerland(self):
        obs = concluding_observations_for_jurisdiction("CH")
        assert len(obs) >= 1
        assert any("CHE" in r.document_symbol for r in obs)

    def test_binding_references_mexico(self):
        refs = binding_references("MX")
        assert len(refs) > 0
        for r in refs:
            assert r.binding_force in (
                BindingForce.BINDING_TREATY,
                BindingForce.BINDING_DOMESTIC,
            )

    def test_doctrine_for_intersectionality_domain(self):
        refs = doctrine_for_domain("intersectionality")
        ids = {r.id for r in refs}
        assert "Crenshaw_1989" in ids

    def test_doctrine_for_legal_capacity_domain(self):
        refs = doctrine_for_domain("legal_capacity")
        assert len(refs) > 0


class TestCitationGeneration:
    def test_legal_style_citation(self):
        citation = generate_citation("IACtHR_Almonacid_2006", style="legal")
        assert "Almonacid" in citation
        assert "2006" in citation
        assert "Series C No. 154" in citation

    def test_apa_style_citation(self):
        citation = generate_citation("IACtHR_Almonacid_2006", style="apa")
        assert "2006" in citation
        assert "Almonacid" in citation

    def test_short_citation(self):
        citation = generate_citation("SCJN_CdT_293_2011", style="short")
        assert "2013" in citation or "293" in citation

    def test_doctrinal_apa(self):
        citation = generate_citation("Crenshaw_1989", style="apa")
        assert "Crenshaw" in citation
        assert "1989" in citation
        assert "Chicago" in citation or "Legal Forum" in citation

    def test_doctrinal_short(self):
        citation = generate_citation("Crenshaw_1989", style="short")
        assert "Crenshaw" in citation
        assert "1989" in citation

    def test_unknown_id_raises(self):
        with pytest.raises(KeyError):
            generate_citation("TOTALLY_MADE_UP")

    def test_default_style_is_legal(self):
        citation_default = generate_citation("CRPD_CO_MEX_2014")
        citation_legal = generate_citation("CRPD_CO_MEX_2014", style="legal")
        assert citation_default == citation_legal
