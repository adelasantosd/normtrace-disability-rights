"""
Tests for normtrace.standards
================================
Verify that CRPD data loads correctly from JSON and is accessible
through the standards API. These tests also serve as integration
tests for the data files.

No LLM calls. I/O is limited to reading the bundled data files.
"""

import pytest
from normtrace.models import (
    BindingForce,
    CRPDArticle,
    GapSeverity,
    GapType,
    GeneralComment,
    ObligationType,
)
from normtrace.standards import (
    ARTICLES,
    GENERAL_COMMENTS,
    PRINCIPLES,
    articles_for_obligation_type,
    articles_with_general_comment,
    cross_cutting_articles,
    get_article,
    get_general_comment,
    get_minimum_standard,
    get_red_flags,
    list_available_articles,
)


class TestArticlesLoad:
    def test_articles_not_empty(self):
        assert len(ARTICLES) > 0

    def test_key_articles_present(self):
        """All analytically critical CRPD articles must be in the corpus."""
        for art_num in (3, 4, 5, 6, 9, 12, 13, 14, 19, 24, 33):
            assert art_num in ARTICLES, f"Article {art_num} missing from corpus"

    def test_article_3_is_cross_cutting(self):
        assert get_article(3).cross_cutting is True

    def test_article_12_not_cross_cutting(self):
        assert get_article(12).cross_cutting is False

    def test_unknown_article_raises(self):
        with pytest.raises(KeyError):
            get_article(99)


class TestArticleContent:
    def test_article_12_has_minimum_standards(self):
        standards = get_minimum_standard(12)
        assert len(standards) > 0
        assert all(s.source_article == 12 for s in standards)

    def test_article_12_has_red_flags(self):
        flags = get_red_flags(12)
        assert len(flags) > 0

    def test_article_12_has_critical_red_flag(self):
        flags = get_red_flags(12)
        critical_flags = [f for f in flags if f.severity_presumption == GapSeverity.CRITICAL]
        assert len(critical_flags) > 0, "Art. 12 must have at least one CRITICAL red flag (guardianship)"

    def test_article_12_red_flag_mentions_guardianship(self):
        flags = get_red_flags(12)
        patterns = " ".join(f.pattern.lower() for f in flags)
        assert "guardianship" in patterns or "tutela" in patterns or "curatorship" in patterns

    def test_article_9_incompatibility_flag(self):
        """Accessibility treated as optional/progressive = INCOMPATIBILITY."""
        flags = get_red_flags(9)
        incompat = [f for f in flags if f.gap_type == GapType.INCOMPATIBILITY]
        assert len(incompat) > 0

    def test_article_14_critical_flag(self):
        flags = get_red_flags(14)
        critical = [f for f in flags if f.severity_presumption == GapSeverity.CRITICAL]
        assert len(critical) > 0, "Art. 14 must have critical flag for disability-based detention"

    def test_article_4_general_obligations(self):
        art = get_article(4)
        assert ObligationType.FULFIL in art.obligation_types
        assert len(art.red_flags) > 0

    def test_article_33_monitoring(self):
        art = get_article(33)
        assert art.cross_cutting is True
        standards = get_minimum_standard(33)
        assert any("independent" in s.description.lower() for s in standards)


class TestGeneralComments:
    def test_all_six_gcs_present(self):
        for gc_id in ("GC_1", "GC_2", "GC_3", "GC_4", "GC_5", "GC_6"):
            assert gc_id in GENERAL_COMMENTS, f"{gc_id} missing from corpus"

    def test_gc1_addresses_article_12(self):
        gc = get_general_comment("GC_1")
        assert gc.article_addressed == 12

    def test_gc2_addresses_article_9(self):
        gc = get_general_comment("GC_2")
        assert gc.article_addressed == 9

    def test_gc3_is_authoritative_interpretation(self):
        gc = get_general_comment("GC_3")
        assert gc.binding_force == BindingForce.AUTHORITATIVE_INTERPRETATION

    def test_gc1_mentions_substituted_decision_making(self):
        gc = get_general_comment("GC_1")
        holdings_text = " ".join(gc.key_holdings).lower()
        assert "substituted" in holdings_text or "guardianship" in holdings_text

    def test_unknown_gc_raises(self):
        with pytest.raises(KeyError):
            get_general_comment("GC_99")


class TestArticleQueries:
    def test_cross_cutting_articles_not_empty(self):
        cc = cross_cutting_articles()
        assert len(cc) > 0
        assert all(a.cross_cutting for a in cc)
        assert any(a.number == 3 for a in cc)
        assert any(a.number == 9 for a in cc)

    def test_articles_with_general_comment(self):
        arts = articles_with_general_comment()
        article_numbers = {a.number for a in arts}
        # Art. 12 (GC_1), Art. 9 (GC_2), Art. 6 (GC_3) etc.
        assert 12 in article_numbers
        assert 9 in article_numbers

    def test_articles_for_fulfil_obligation(self):
        arts = articles_for_obligation_type(ObligationType.FULFIL)
        # Arts. 19, 24, 33 all generate fulfilment obligations
        numbers = {a.number for a in arts}
        assert 19 in numbers
        assert 24 in numbers

    def test_list_available_articles_sorted(self):
        available = list_available_articles()
        assert available == sorted(available)
        assert 3 in available
        assert 12 in available


class TestPrinciples:
    def test_eight_principles_loaded(self):
        assert len(PRINCIPLES) == 8

    def test_dignity_principle_present(self):
        labels = [p.label for p in PRINCIPLES]
        assert "dignity" in labels

    def test_accessibility_principle_present(self):
        labels = [p.label for p in PRINCIPLES]
        assert "accessibility" in labels
