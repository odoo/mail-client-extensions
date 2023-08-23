# -*- coding: utf-8 -*-

import re

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("16.0")
class TestReportalypse(UpgradeCase):
    # -------------------------------------------------------------------------
    # TESTS
    # -------------------------------------------------------------------------

    def _prepare_test_custom_fin_report_migrated(self):
        report = self.env["account.financial.html.report"].create(
            {
                "name": "Custom Financial Report Test 1",
                "country_id": self.env["res.country"].search([("name", "=", "Belgium")]).id,
            }
        )
        report_vals = {
            "name": report.name,
            "country_id": report.country_id.id,
        }

        afhrl = self.env["account.financial.html.report.line"]

        # - root-level line with aggregation formula
        line1 = afhrl.create(
            {
                "code": "custom_code_1",
                "financial_report_id": report.id,
                "formulas": "custom_code_2 + custom_code_3",
                "level": 1,
                "name": "Custom Financial Report Line Test 1",
            }
        )
        line1_vals = {
            "code": line1.code,
            "name": line1.name,
            "hierarchy_level": line1.level,
            "formula": line1.formulas,
        }

        # - non-root level line (got a parent_id) and domain formula
        line2 = afhrl.create(
            {
                "code": "custom_code_2",
                "domain": "[('account_id.user_type_id', '=', 13)]",
                "formulas": "-sum",
                "level": 2,
                "name": "Custom Financial Report Line Test 2",
                "parent_id": line1.id,
            }
        )
        line2_vals = {
            "code": line2.code,
            "hierarchy_level": 3,
            "formula": line2.formulas,
            "name": line2.name,
            "parent_name": line2.parent_id.name,
        }

        # --- The following two lines (line3 and line4) are added to test the migration of `sum_if_(pos|neg)_groupby` formulas
        # --- under the simplifying assumption (that holds true for standard records in v15) that domains can only take one of
        # --- two forms (A and B) defined in the following

        # - line with non-root parent line and sum_if_pos_groupby formula with domain of type A
        # Domains of type A are assumed to contain at most 1 '!', basically splitting patterns (to match) from antipatterns (to avoid)
        # They can be expressed as:             (p1 OR … OR pN) AND !(pM OR … OR pL)
        # which is known to be equivalent to:   (p1 OR … OR pN) AND (!pM AND … AND !pL)
        groupby_domain_l3_v15 = (  # (428 OR 445) AND (!4287 AND !4288 AND !4452)
            "['|', ('account_id.code', '=like', '428%'), ('account_id.code', '=like', '445%'),"
            " '!', '|', ('account_id.code', '=like', '4287%'), '|', ('account_id.code', '=like', '4288%'), ('account_id.code', '=like', '4452%')]"
        )
        # Some notes (regarding the Odoo 16) equivalent:
        #   * D (aka debit), is used (as opposed to C, aka credit) for `sum_if_pos_groupby` (as opposed to `sum_if_neg_groupby`)
        #   * Numbers outside parentheses are patterns of account codes that should be matched (e.g. SQL-style 428% should be matched…)
        #   * Numbers inside the `\()` parentheses are antipatterns of account codes not to match (e.g. …however SQL-style 4287% should not)
        groupby_domain_l3_v16 = r"428\(4287,4288)D + 445\(4452)D"
        line3 = afhrl.create(
            {
                "code": "custom_code_3",
                "domain": groupby_domain_l3_v15,
                "formulas": "sum_if_pos_groupby",
                "groupby": "account_id",
                "level": 3,
                "name": "Custom Financial Report Line Test 3",
                "parent_id": line2.id,
            }
        )
        line3_vals = {
            "code": line3.code,
            "domain_16": groupby_domain_l3_v16,
            "hierarchy_level": 5,
            "name": line3.name,
            "parent_name": line3.parent_id.name,
        }

        # - root line with `sum_if_neg_groupby` formula, using domain of type B
        # Domains of type B are conjunctions (OR-expression) of disjunctions (AND-expressions) of - potentially - a pattern and its antipatterns.
        # with antipatterns using the `not like` comparator and patterns using the `=like` one.
        groupby_domain_l4_v15 = (  # (40 AND !406) OR (50)
            "[('account_id.code', '=like', '40%'), '|', ('account_id.code', 'not like', '406%'),"
            " ('account_id.code', '=like', '50%')]"
        )
        groupby_domain_l4_v16 = r"-40\(406)C - 50C"  # negated due to the `-` in the `formulas`: -sum_if_neg_groupby
        line4 = afhrl.create(
            {
                "code": "custom_code_4",
                "domain": groupby_domain_l4_v15,
                "financial_report_id": report.id,
                "formulas": "-sum_if_neg_groupby",
                "groupby": "account_id",
                "level": 1,
                "name": "Custom Financial Report Line Test 4",
            }
        )
        line4_vals = {
            "code": line4.code,
            "domain_16": groupby_domain_l4_v16,
            "hierarchy_level": line4.level,
            "name": line4.name,
        }

        return report_vals, line1_vals, line2_vals, line3_vals, line4_vals

    def _check_test_custom_fin_report_migrated(self, rep_vals, l1_vals, l2_vals, l3_vals, l4_vals):
        report = self.env["account.report"].search([("name", "=", rep_vals["name"])])
        self.assertTrue(report)
        self.assertEqual(report.country_id.id, rep_vals["country_id"])

        column = self.env["account.report.column"].search([("report_id", "=", report.id)])
        self.assertTrue(column)

        arl = self.env["account.report.line"]
        are = self.env["account.report.expression"]

        l1 = arl.search([("report_id", "=", report.id), ("name", "=", l1_vals["name"])])
        self.assertTrue(l1)
        self.assertEqual(l1.hierarchy_level, l1_vals["hierarchy_level"])
        self.assertEqual(l1.code, l1_vals["code"])
        self.assertFalse(l1.parent_id)

        e1 = are.search([("report_line_id", "=", l1.id)])
        self.assertTrue(e1)
        self.assertEqual(e1.label, "balance")
        self.assertEqual(e1.engine, "aggregation")
        self.assertEqual(e1.formula, re.sub(r"(\w+)", r"\1.balance", l1_vals["formula"]))
        self.assertEqual(e1.subformula, "cross_report")

        l2 = arl.search([("report_id", "=", report.id), ("name", "=", l2_vals["name"])])
        self.assertTrue(l2)
        self.assertEqual(l2.hierarchy_level, l2_vals["hierarchy_level"])
        self.assertEqual(l2.parent_id.name, l2_vals["parent_name"])
        self.assertEqual(l2.code, l2_vals["code"])

        e2 = are.search([("report_line_id", "=", l2.id)])
        self.assertTrue(e2)
        self.assertEqual(e2.label, "balance")
        self.assertEqual(e2.engine, "domain")
        self.assertEqual(e2.subformula, l2_vals["formula"])
        # subformula will contain the domain however it's hard to check as it also gets adapted during the upgrade

        l3 = arl.search([("report_id", "=", report.id), ("name", "=", l3_vals["name"])])
        self.assertTrue(l3)
        self.assertEqual(l3.hierarchy_level, l3_vals["hierarchy_level"])
        self.assertEqual(l3.parent_id.name, l3_vals["parent_name"])
        self.assertEqual(l3.code, l3_vals["code"])

        e3 = are.search([("report_line_id", "=", l3.id)])
        self.assertTrue(e3)
        self.assertEqual(e3.label, "balance")
        self.assertEqual(e3.engine, "account_codes")
        self.assertEqual(e3.formula, l3_vals["domain_16"])
        self.assertFalse(e3.subformula)

        l4 = arl.search([("report_id", "=", report.id), ("name", "=", l4_vals["name"])])
        self.assertTrue(l4)
        self.assertEqual(l4.hierarchy_level, l4_vals["hierarchy_level"])
        self.assertEqual(l4.code, l4_vals["code"])
        self.assertFalse(l4.parent_id)

        e4 = are.search([("report_line_id", "=", l4.id)])
        self.assertTrue(e4)
        self.assertEqual(e4.label, "balance")
        self.assertEqual(e4.engine, "account_codes")
        self.assertEqual(e4.formula, l4_vals["domain_16"])
        self.assertFalse(e4.subformula)

    # -------------------------------------------------------------------------
    # SETUP
    # -------------------------------------------------------------------------

    def prepare(self):
        return [("_check_test_custom_fin_report_migrated", self._prepare_test_custom_fin_report_migrated())]

    def check(self, tests):
        for check_method, test_params in tests:
            getattr(self, check_method)(*test_params)
