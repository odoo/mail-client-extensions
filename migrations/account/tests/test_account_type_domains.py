# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~15.5")
class TestAccountTypeDomains(UpgradeCase):
    def prepare(self):
        domains_dict = {
            "1": [
                [("user_type_id.type", "in", ["payable", "liquidity"])],
                "[('account_type', 'in', ['liability_payable', 'asset_cash', 'liability_credit_card'])]",
            ],
            "2": [[("user_type_id.type", "=", "receivable")], "[('account_type', '=', 'asset_receivable')]"],
            "3": [
                [("user_type_id.type", "=", "liquidity")],
                "[('account_type', 'in', ('asset_cash', 'liability_credit_card'))]",
            ],
            "4": [
                [("user_type_id", "=", util.ref(self.env.cr, "account.data_account_type_receivable"))],
                "[('account_type', '=', 'asset_receivable')]",
            ],
            "5": [
                [
                    (
                        "user_type_id",
                        "in",
                        [
                            util.ref(self.env.cr, "account.data_account_type_non_current_assets"),
                            util.ref(self.env.cr, "account.data_account_type_current_assets"),
                        ],
                    )
                ],
                "[('account_type', 'in', ['asset_non_current', 'asset_current'])]",
            ],
        }

        models = [
            "account.account",
            "account.account.template",
        ]

        results = self.env["ir.actions.act_window"].create(
            [{"name": k, "domain": v[0], "res_model": model} for k, v in domains_dict.items() for model in models]
        )
        return {"result_ids": results.ids, "domains": domains_dict}

    def check(self, init):
        domains_dict = init["domains"]
        for result in self.env["ir.actions.act_window"].browse(init["result_ids"]):
            self.assertEqual(result.domain, domains_dict[result.name][1])
