import ast
import re

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.3")
class TestAccountRuleTypeToBoolean(UpgradeCase, abstract=True):
    def prepare(self):
        companies = self.env["res.company"].create(
            {"name": "test company 1", "country_id": self.env.ref("base.us").id, "rule_type": "invoice_and_refund"},
            {"name": "test company 2", "country_id": self.env.ref("base.us").id, "rule_type": "not_synchronize"},
        )

        search_view = self.env["ir.ui.view"].create(
            {
                "name": "res.company.search",
                "type": "search",
                "model": "res.company",
                "arch": """
                        <search>
                            <filter name="rule_type" domain="[('rule_type', '=', 'invoice_and_refund')]" />
                            <filter name="rule_type_2" domain="[('rule_type', '!=', 'invoice_and_refund')]" />
                            <filter name="rule_type_3" domain="[('rule_type', '=', 'not_synchronize')]" />
                        </search>
                    """,
            }
        )

        company_with_invoice_refund = self.env["res.company"].search(["rule_type", "=", "invoice_and_refund"])

        return companies.ids, search_view.id, company_with_invoice_refund.id

    def check(self, init):
        company_ids, search_view_id, company_with_invoice_refund_id = init
        company_invoice_refund, company_not_synchro = self.env["res.company"].browse(company_ids)
        view = self.env["ir.ui.view"].browse(search_view_id)

        self.assertTrue(company_invoice_refund.intercompany_generate_bills_refund)
        self.assertFalse(company_not_synchro.intercompany_generate_bills_refund)

        company_with_invoice_refund = self.env["res.company"].search(["intercompany_generate_bills_refund", "=", True])
        self.assertEqual(company_with_invoice_refund.id, company_with_invoice_refund_id)

        domains_regex = re.compile(r"domain=\"(.*?)\"")
        company_search_view_domains = domains_regex.findall(view.arch)
        expected_company_search_view_domains = [
            [("intercompany_generate_bills_refund", "=", True)],
            [("intercompany_generate_bills_refund", "!=", True)],
            [("intercompany_generate_bills_refund", "=", False)],
        ]

        for domain_str, expected_domain in zip(company_search_view_domains, expected_company_search_view_domains):
            domain = ast.literal_eval(domain_str)
            self.assertEqual(domain, expected_domain)
