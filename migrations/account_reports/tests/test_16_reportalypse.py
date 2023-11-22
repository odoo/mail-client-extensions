import re

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("16.0")
class TestReportalypse(UpgradeCase):
    # -------------------------------------------------------------------------
    # TESTS
    # -------------------------------------------------------------------------

    def _prepare_test_custom_fin_report_migrated(self):
        afhr = self.env["account.financial.html.report"]
        afhrl = self.env["account.financial.html.report.line"]

        report1 = afhr.create(
            {
                "name": "Custom Financial Report Test 1",
                "country_id": self.env["res.country"].search([("name", "=", "Belgium")]).id,
            }
        )
        report1_vals = {
            "name": report1.name,
            "country_id": report1.country_id.id,
        }

        # - root-level line with aggregation formula and a refernce to a line in another report (`subformula` = "cross_report")
        line1 = afhrl.create(
            {
                "code": "custom_code_1",
                "financial_report_id": report1.id,
                "formulas": "custom_code_2 + custom_code_3 + custom_code_5",
                "level": 1,
                "name": "Custom Financial Report Line Test 1",
            }
        )
        line1_vals = {
            "code": line1.code,
            "name": line1.name,
            "hierarchy_level": line1.level,
            "formula": line1.formulas,
            "subformula": "cross_report",
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
            "subformula": line2.formulas,
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
                "financial_report_id": report1.id,
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

        report2 = afhr.create(
            {
                "name": "Custom Financial Report Test 2",
                "country_id": self.env["res.country"].search([("name", "=", "Italy")]).id,
            }
        )
        report2_vals = {
            "name": report2.name,
            "country_id": report2.country_id.id,
        }

        line5 = afhrl.create(
            {
                "code": "custom_code_5",
                "financial_report_id": report2.id,
                "formulas": "custom_code_6",
                "level": 1,
                "name": "Custom Financial Report Line Test 5",
            }
        )
        line5_vals = {
            "code": line5.code,
            "name": line5.name,
            "hierarchy_level": line5.level,
            "formula": line5.formulas,
        }

        line6 = afhrl.create(
            {
                "code": "custom_code_6",
                "domain": "[('account_id.user_type_id', '=', 13)]",
                "formulas": "-sum",
                "level": 2,
                "name": "Custom Financial Report Line Test 6",
                "parent_id": line5.id,
            }
        )
        line6_vals = {
            "code": line6.code,
            "hierarchy_level": 3,
            "subformula": line6.formulas,
            "name": line6.name,
            "parent_name": line6.parent_id.name,
        }

        return report1_vals, report2_vals, line1_vals, line2_vals, line3_vals, line4_vals, line5_vals, line6_vals

    def _check_test_custom_fin_report_migrated(
        self, rep1_vals, rep2_vals, l1_vals, l2_vals, l3_vals, l4_vals, l5_vals, l6_vals
    ):
        ar = self.env["account.report"]
        arc = self.env["account.report.column"]
        arl = self.env["account.report.line"]
        are = self.env["account.report.expression"]

        report1 = ar.search([("name", "=", rep1_vals["name"]), ("country_id", "=", rep1_vals["country_id"])])
        self.assertTrue(report1)

        column1 = arc.search([("report_id", "=", report1.id)])
        self.assertTrue(column1)

        l1 = arl.search(
            [
                ("report_id", "=", report1.id),
                ("name", "=", l1_vals["name"]),
                ("hierarchy_level", "=", l1_vals["hierarchy_level"]),
                ("code", "=", l1_vals["code"]),
                ("parent_id", "=", False),
            ]
        )
        self.assertTrue(l1)

        e1 = are.search(
            [
                ("report_line_id", "=", l1.id),
                ("label", "=", "balance"),
                ("engine", "=", "aggregation"),
                ("formula", "=", re.sub(r"(\w+)", r"\1.balance", l1_vals["formula"])),
                ("subformula", "=", l1_vals["subformula"]),
            ]
        )
        self.assertTrue(e1)

        l2 = arl.search(
            [
                ("report_id", "=", report1.id),
                ("name", "=", l2_vals["name"]),
                ("hierarchy_level", "=", l2_vals["hierarchy_level"]),
                ("code", "=", l2_vals["code"]),
            ]
        )
        self.assertTrue(l2)
        self.assertEqual(l2.parent_id.name, l2_vals["parent_name"])

        e2 = are.search(
            [
                ("report_line_id", "=", l2.id),
                ("label", "=", "balance"),
                ("engine", "=", "domain"),
                # formula will contain the domain however it's hard to check as it also gets adapted during the upgrade
                ("subformula", "=", l2_vals["subformula"]),
            ]
        )
        self.assertTrue(e2)

        l3 = arl.search(
            [
                ("report_id", "=", report1.id),
                ("name", "=", l3_vals["name"]),
                ("hierarchy_level", "=", l3_vals["hierarchy_level"]),
                ("code", "=", l3_vals["code"]),
            ]
        )
        self.assertTrue(l3)
        self.assertEqual(l3.parent_id.name, l3_vals["parent_name"])

        e3 = are.search(
            [
                ("report_line_id", "=", l3.id),
                ("label", "=", "balance"),
                ("engine", "=", "account_codes"),
                ("formula", "=", l3_vals["domain_16"]),
                ("subformula", "=", False),
            ]
        )
        self.assertTrue(e3)

        l4 = arl.search(
            [
                ("report_id", "=", report1.id),
                ("name", "=", l4_vals["name"]),
                ("hierarchy_level", "=", l4_vals["hierarchy_level"]),
                ("code", "=", l4_vals["code"]),
                ("parent_id", "=", False),
            ]
        )
        self.assertTrue(l4)

        e4 = are.search(
            [
                ("report_line_id", "=", l4.id),
                ("label", "=", "balance"),
                ("engine", "=", "account_codes"),
                ("formula", "=", l4_vals["domain_16"]),
                ("subformula", "=", False),
            ]
        )
        self.assertTrue(e4)

        report2 = ar.search([("name", "=", rep2_vals["name"]), ("country_id", "=", rep2_vals["country_id"])])
        self.assertTrue(report2)

        column2 = arc.search([("report_id", "=", report2.id)])
        self.assertTrue(column2)

        l5 = arl.search(
            [
                ("report_id", "=", report2.id),
                ("name", "=", l5_vals["name"]),
                ("hierarchy_level", "=", l5_vals["hierarchy_level"]),
                ("code", "=", l5_vals["code"]),
                ("parent_id", "=", False),
            ]
        )
        self.assertTrue(l5)

        e5 = are.search(
            [
                ("report_line_id", "=", l5.id),
                ("label", "=", "balance"),
                ("engine", "=", "aggregation"),
                ("formula", "=", re.sub(r"(\w+)", r"\1.balance", l5_vals["formula"])),
                ("subformula", "=", False),
            ]
        )
        self.assertTrue(e5)

        l6 = arl.search(
            [
                ("report_id", "=", report2.id),
                ("name", "=", l6_vals["name"]),
                ("hierarchy_level", "=", l6_vals["hierarchy_level"]),
                ("code", "=", l6_vals["code"]),
            ]
        )
        self.assertTrue(l6)
        self.assertEqual(l6.parent_id.name, l6_vals["parent_name"])

        e6 = are.search(
            [
                ("report_line_id", "=", l6.id),
                ("label", "=", "balance"),
                ("engine", "=", "domain"),
                ("subformula", "=", l6_vals["subformula"]),
            ]
        )
        self.assertTrue(e6)

    # -------------------------------------------------------------------------
    # SETUP
    # -------------------------------------------------------------------------

    def prepare(self):
        return [("_check_test_custom_fin_report_migrated", self._prepare_test_custom_fin_report_migrated())]

    def check(self, tests):
        for check_method, test_params in tests:
            getattr(self, check_method)(*test_params)
