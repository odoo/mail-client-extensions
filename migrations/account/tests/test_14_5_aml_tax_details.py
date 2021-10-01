# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~14.5")
class TestAmlTaxDetails(UpgradeCase):

    # -------------------------------------------------------------------------
    # TESTS
    # -------------------------------------------------------------------------

    def _prepare_test_1_group_of_taxes(self):
        percent_tax = self.env["account.tax"].create(
            {
                "name": "percent_tax",
                "amount_type": "percent",
                "amount": 10.0,
                "type_tax_use": "none",
            }
        )
        tax_group = self.env["account.tax"].create(
            {
                "name": "tax_group",
                "amount_type": "group",
                "children_tax_ids": [(6, 0, percent_tax.ids)],
            }
        )

        move_type_field = "move_type" if util.version_gte("saas~13.3") else "type"
        invoice = self.env["account.move"].create(
            {
                move_type_field: "out_invoice",
                "partner_id": self.partner.id,
                "invoice_date": "2016-01-01",
                "date": "2016-01-01",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "line",
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "account_id": self.account_income.id,
                            "tax_ids": [(6, 0, tax_group.ids)],
                        },
                    )
                ],
            }
        )
        invoice.action_post()
        return [invoice.id]

    def _check_test_1_group_of_taxes(self, config, invoice_id):
        invoice = self.env["account.move"].browse(invoice_id)
        tax_lines = invoice.line_ids.filtered("group_tax_id")
        self.assertTrue(tax_lines)

    # -------------------------------------------------------------------------
    # SETUP
    # -------------------------------------------------------------------------

    def prepare(self):
        test_name = "TestAmlTaxDetails"
        self.company = self.env["res.company"].create(
            {
                "name": f"company for {test_name}",
                "user_ids": [(4, self.env.ref("base.user_admin").id)],
            }
        )

        # Create user.
        user = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "user %s" % test_name,
                    "login": test_name,
                    "groups_id": [
                        (6, 0, self.env.user.groups_id.ids),
                        (4, self.env.ref("account.group_account_user").id),
                    ],
                    "company_ids": [(6, 0, self.company.ids)],
                    "company_id": self.company.id,
                }
            )
        )
        user.partner_id.email = "%s@test.com" % test_name

        self.env = self.env(user=user)
        self.cr = self.env.cr

        chart_template = self.env.ref("l10n_generic_coa.configurable_chart_template", raise_if_not_found=False)
        if not chart_template:
            self.skipTest("Accounting Tests skipped because the user's company has no chart of accounts.")

        chart_template.try_loading(company=self.company)

        revenue = self.env.ref("account.data_account_type_revenue").id
        self.account_income = self.env["account.account"].search(
            [("company_id", "=", self.company.id), ("user_type_id", "=", revenue)],
            limit=1,
        )
        self.account_receivable = self.env["account.account"].search(
            [("company_id", "=", self.company.id), ("user_type_id.type", "=", "receivable")],
            limit=1,
        )

        # Setup partner.
        self.partner = self.env["res.partner"].create(
            {
                "name": "Test partner %s" % test_name,
                "property_account_receivable_id": self.account_receivable.id,
                "company_id": self.company.id,
            }
        )

        return {
            "tests": [
                self._prepare_test_1_group_of_taxes(),
            ],
            "config": {
                "company_id": self.company.id,
                "partner_id": self.partner.id,
                "account_receivable_id": self.account_receivable.id,
            },
        }

    def check(self, init):
        config = init["config"]
        self._check_test_1_group_of_taxes(config, *init["tests"][0])
