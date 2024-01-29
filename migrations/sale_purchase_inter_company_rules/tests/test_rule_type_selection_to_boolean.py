import ast
import re

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.3")
class TestSalePurchaseRuleTypeToBoolean(UpgradeCase, abstract=True):
    def prepare(self):
        companies = self.env["res.company"].create(
            [
                {"name": "test company 1", "country_id": self.env.ref("base.us").id, "rule_type": "sale"},
                {"name": "test company 2", "country_id": self.env.ref("base.us").id, "rule_type": "purchase"},
                {"name": "test company 3", "country_id": self.env.ref("base.us").id, "rule_type": "sale_purchase"},
                {"name": "test company 4", "country_id": self.env.ref("base.us").id, "rule_type": "not_synchronize"},
            ]
        )

        search_view = self.env["ir.ui.view"].create(
            {
                "name": "res.company.search",
                "type": "search",
                "model": "res.company",
                "arch": """
                        <search>
                            <filter name="rule_type" domain="[('rule_type', '=', 'sale')]" />
                            <filter name="rule_type_2" domain="[('rule_type', '!=', 'sale')]" />
                            <filter name="rule_type_3" domain="[('rule_type', '=', 'sale_purchase')]" />
                            <filter name="rule_type_4" domain="[('rule_type', '=', 'purchase')]" />
                            <filter name="rule_type_5" domain="[('rule_type', '=', 'not_synchronize')]" />
                        </search>
                    """,
            }
        )

        company_with_sale = self.env["res.company"].search(["rule_type", "in", ["sale", "sale_purchase"]])
        company_with_purchase = self.env["res.company"].search(["rule_type", "in", ["purchase", "sale_purchase"]])

        return companies.ids, search_view.id, company_with_sale.ids, company_with_purchase.ids

    def check(self, init):
        company_ids, search_view_id, company_with_sale_ids, company_with_purchase_ids = init
        companies = self.env["res.company"].browse(company_ids)
        view = self.env["ir.ui.view"].browse(search_view_id)

        self.assertTrue(companies[0].intercompany_generate_sales_orders)
        self.assertFalse(companies[0].intercompany_generate_purchase_orders)

        self.assertFalse(companies[1].intercompany_generate_sales_orders)
        self.assertTrue(companies[1].intercompany_generate_purchase_orders)

        self.assertTrue(companies[2].intercompany_generate_sales_orders)
        self.assertTrue(companies[2].intercompany_generate_purchase_orders)

        self.assertFalse(companies[3].intercompany_generate_sales_orders)
        self.assertFalse(companies[3].intercompany_generate_purchase_orders)

        company_with_sale = self.env["res.company"].search(["intercompany_generate_sales_orders", "=", True])
        self.assertEqual(company_with_sale.ids, company_with_sale_ids)
        company_with_purchase = self.env["res.company"].search(["intercompany_generate_purchase_orders", "=", True])
        self.assertEqual(company_with_purchase.ids, company_with_purchase_ids)

        domains_regex = re.compile(r"domain=\"(.*?)\"")
        company_search_view_domains = domains_regex.findall(view.arch)
        expected_company_search_view_domains = [
            [("intercompany_generate_sales_orders", "=", True)],
            [("intercompany_generate_sales_orders", "!=", True)],
            [
                "&",
                ("intercompany_generate_sales_orders", "=", True),
                ("intercompany_generate_purchase_orders", "=", True),
            ],
            [("intercompany_generate_purchase_orders", "=", True)],
            [
                "|",
                "|",
                ("intercompany_generate_bills_refund", "=", False),
                ("intercompany_generate_sales_orders", "=", False),
                ("intercompany_generate_purchase_orders", "=", False),
            ],
        ]

        for domain_str, expected_domain in zip(company_search_view_domains, expected_company_search_view_domains):
            domain = ast.literal_eval(domain_str)
            self.assertEqual(domain, expected_domain)
