"""Regression tests for product classification vs. UI constraints."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import core
import design_system
from design_system import DesignSystemGenerator


class TestProductClassificationQuery(unittest.TestCase):
    def test_reported_salon_query_resolves_to_beauty_not_veterinary(self):
        result = core.search(
            "salon booking services accessible mobile", "product", 1,
            diagnostics=True,
        )
        self.assertEqual("Beauty/Spa/Wellness Service",
                         result["results"][0]["Product Type"])
        self.assertEqual("salon booking services", result["diagnostics"]["search_query"])

    def test_accessibility_and_responsive_modifiers_do_not_change_category(self):
        queries = (
            "salon booking services accessible",
            "salon booking services ACCESSIBILITY responsive",
            "salon booking services W.C.A.G. mobile",
        )
        for query in queries:
            with self.subTest(query=query):
                result = core.search(query, "product", 1)
                self.assertEqual("Beauty/Spa/Wellness Service",
                                 result["results"][0]["Product Type"])

    def test_mobile_alone_is_preserved_as_a_possible_business_attribute(self):
        result = core.search("mobile salon booking", "product", 1, diagnostics=True)
        self.assertIn("mobile", result["diagnostics"]["search_query"])

    def test_mobile_is_removed_when_paired_with_explicit_accessibility_constraint(self):
        result = core.search(
            "mobile salon booking accessible", "product", 1, diagnostics=True
        )
        self.assertEqual("salon booking", result["diagnostics"]["search_query"])
        self.assertEqual("Beauty/Spa/Wellness Service",
                         result["results"][0]["Product Type"])

    def test_constraint_only_query_abstains_instead_of_inventing_a_category(self):
        result = core.search(
            "accessible responsive mobile WCAG keyboard navigation",
            "product", 1, diagnostics=True,
        )
        self.assertEqual([], result["results"])
        self.assertEqual(0, result["count"])
        self.assertEqual("no-classification-signal",
                         result["diagnostics"]["reason"])
        generated = DesignSystemGenerator().generate("accessible responsive mobile")
        self.assertEqual("General", generated["category"])
        self.assertTrue(generated["reasoning_default"])

    def test_held_out_spa_paraphrase_still_resolves(self):
        result = core.search(
            "calming salon for massages facials and appointment reservations",
            "product", 1,
        )
        self.assertEqual("Beauty/Spa/Wellness Service",
                         result["results"][0]["Product Type"])

    def test_explicit_beauty_spa_query_still_resolves(self):
        result = core.search("beauty spa wellness booking landing page", "product", 1)
        self.assertEqual("Beauty/Spa/Wellness Service",
                         result["results"][0]["Product Type"])

    def test_dental_industry_category_is_preserved_with_mobile_constraints(self):
        result = core.search(
            "dental booking services accessible mobile", "product", 1
        )
        self.assertEqual("Dental Practice", result["results"][0]["Product Type"])

    def test_healthcare_industry_category_is_preserved(self):
        result = core.search(
            "accessible healthcare analytics dashboard for patients",
            "product", 1,
        )
        self.assertEqual("Healthcare App", result["results"][0]["Product Type"])

    def test_fintech_and_saas_categories_are_preserved(self):
        finance = core.search(
            "fintech banking app with a secure dark dashboard", "product", 1
        )
        saas = core.search("SaaS dashboard for a B2B cloud product", "product", 1)
        self.assertEqual("Fintech/Crypto", finance["results"][0]["Product Type"])
        self.assertEqual("SaaS (General)", saas["results"][0]["Product Type"])

    def test_end_to_end_generation_keeps_full_query_for_style_search(self):
        query = "salon booking services accessible mobile"
        calls = []

        def recording_search(search_query, *args, **kwargs):
            calls.append((search_query, args[0] if args else kwargs.get("domain")))
            return core.search(search_query, *args, **kwargs)

        with patch.object(design_system, "search", side_effect=recording_search):
            generated = DesignSystemGenerator().generate(query)

        self.assertEqual("Beauty/Spa/Wellness Service", generated["category"])
        self.assertEqual("Soft UI Evolution", generated["style"]["name"])
        self.assertTrue(any(domain == "style" and query in search_query
                            for search_query, domain in calls))

    def test_non_product_domain_receives_the_unmodified_query(self):
        query = "salon booking services accessible mobile"
        result = core.search(query, "style", 1, diagnostics=True)
        self.assertEqual(query, result["diagnostics"]["search_query"])


if __name__ == "__main__":
    unittest.main()
