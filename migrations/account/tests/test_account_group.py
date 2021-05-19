# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("13.1")
class AccountGroupPerCompanyCase(UpgradeCase):
    """
    Before SaaS-12.4 we don't have company id in account group
    So we check here that group link with account.account
    company is same as group company and name of that group.
    """

    def prepare(self):
        test_name = "TestAcccountGroup"

        company = self.env["res.company"].create({"name": "company for %s" % test_name})
        company_2 = self.env["res.company"].create({"name": "company_2 for %s" % test_name})

        # Create user.
        account_user = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "user %s" % test_name,
                    "login": test_name,
                    "groups_id": [
                        (6, 0, self.env.user.groups_id.ids),
                        (4, self.env.ref("account.group_account_manager").id),
                    ],
                    "company_ids": [(6, 0, (company + company_2).ids)],
                    "company_id": company.id,
                }
            )
        )
        account_user.partner_id.email = "%s@test.com" % test_name

        env = self.env(user=account_user)

        chart_template = env.ref("l10n_generic_coa.configurable_chart_template", raise_if_not_found=False)
        if not chart_template:
            self.skipTest("Accounting Tests skipped because the user's company has no chart of accounts.")

        chart_template.try_loading(company=company)
        chart_template.try_loading(company=company_2)

        account_ids = env["account.account"]
        AccountGroup = env["account.group"]
        parent_group = AccountGroup.create({"name": "Group 10", "code_prefix": "10"})
        group_1 = AccountGroup.create(
            {
                "name": "Group 101",
                "code_prefix": "101",
                "parent_id": parent_group.id,
            }
        )
        group_2 = AccountGroup.create(
            {
                "name": "Group 102",
                "code_prefix": "102",
                "parent_id": parent_group.id,
            }
        )

        account_codes_and_group = [("1011", group_1), ("1012", group_1), ("1021", group_2), ("1022", group_2)]
        for code, group in account_codes_and_group:
            account_ids += env["account.account"].create(
                {
                    "code": code,
                    "name": "Test  Account %s" % (code),
                    "company_id": company.id,
                    "group_id": group.id,
                    "user_type_id": env.ref("account.data_account_type_expenses").id,
                }
            )
            account_ids += env["account.account"].create(
                {
                    "code": code,
                    "name": "Test  Account %s" % (code),
                    "company_id": company_2.id,
                    "group_id": group.id,
                    "user_type_id": env.ref("account.data_account_type_expenses").id,
                }
            )
        return {"account_ids": [(a.id, a.group_id.name) for a in account_ids]}

    def check(self, init):
        for account_id, group_name in init["account_ids"]:
            account = self.env["account.account"].browse(account_id)
            self.assertEqual(account.company_id, account.group_id.company_id)
            self.assertEqual(account.company_id, account.group_id.parent_id.company_id)
            self.assertEqual(group_name, account.group_id.name)
