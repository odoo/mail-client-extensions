# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase
from odoo.addons.base.maintenance.migrations.util import version_gte


class TestAccountingSetupCommon(UpgradeCase, abstract=True):
    def _get_tax_by_xml_id(self, module, xml_id):
        """Helper to retrieve a tax easily from a chart template.

        :param module:  The module to which the tax belongs.
        :param xml_id:  The tax's xml id.
        :return:        An account.tax record
        """
        return self.env.ref(f"{module}.{self.env.company.id}_{xml_id}")

    def _get_account(self, domain):
        return self.env["account.account"].search(
            ["&", ("company_id", "=", self.company.id)] + domain,
            limit=1,
        )

    def prepare(self, chart_template_ref="l10n_generic_coa.configurable_chart_template"):
        test_name = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        self.company = self.env["res.company"].create(
            {
                "name": f"company for {test_name}",
                "user_ids": [(4, self.env.ref("base.user_admin").id)],
                "country_id": self.env.ref("base.us").id,
            }
        )

        # Create user.
        user = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": f"user {test_name}",
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
        user.partner_id.email = f"{test_name}@test.com"

        self.env = self.env(user=user)
        self.cr = self.env.cr

        chart_template = self.env.ref(chart_template_ref, raise_if_not_found=False)
        if not chart_template:
            self.skipTest("Accounting Tests skipped because the user's company has no chart of accounts.")

        chart_template.sudo().try_loading(company=self.company)

        if version_gte("16.0"):
            income_domain = [("account_type", "=", "income")]
            receivable_domain = [("account_type", "=", "asset_receivable")]
            payable_domain = [("account_type", "=", "liability_payable")]
        else:
            revenue = self.env.ref("account.data_account_type_revenue").id
            income_domain = [("user_type_id", "=", revenue)]
            receivable_domain = [("user_type_id.type", "=", "receivable")]
            payable_domain = [("user_type_id.type", "=", "payable")]

        self.account_income = self._get_account(income_domain)
        self.account_receivable = self._get_account(receivable_domain)
        self.account_payable = self._get_account(payable_domain)

        self.partner = self.env["res.partner"].create(
            {
                "name": f"Test partner {test_name}",
                "property_account_receivable_id": self.account_receivable.id,
                "property_account_payable_id": self.account_payable.id,
                "company_id": self.company.id,
            }
        )

        return {
            "tests": [],
            "config": {
                "company_id": self.company.id,
                "partner_id": self.partner.id,
                "account_receivable_id": self.account_receivable.id,
                "account_payable_id": self.account_payable.id,
            },
        }

    def check(self, init):
        config = init["config"]
        for check_method, test_params in init["tests"]:
            getattr(self, check_method)(config, *test_params)
