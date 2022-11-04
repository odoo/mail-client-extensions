# -*- coding: utf-8 -*-

from freezegun import freeze_time

from odoo import fields

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("16.0")
class AssetsRevampingCase(UpgradeCase):
    def prepare(self):
        with freeze_time("2020-10-06"):
            account_asset, account_asset_depreciation_expense, account_depreciation = self.env[
                "account.account"
            ].create(
                [
                    {
                        "name": "_UPG_ fixed assets",
                        "user_type_id": self.env.ref("account.data_account_type_current_assets").id,
                        "code": "999241000",
                    },
                    {
                        "name": "_UPG_ assets depreciation",
                        "code": "999241009",
                        "user_type_id": self.env.ref("account.data_account_type_expenses").id,
                    },
                    {
                        "name": "_UPG_ assets depreciation expense",
                        "code": "999630200",
                        "user_type_id": self.env.ref("account.data_account_type_current_assets").id,
                    },
                ]
            )
            journal = self.env["account.journal"].create(
                {"name": "_UPG_ miscellaneous", "type": "general", "code": "UPG_M"}
            )
            asset = (
                self.env["account.asset"]
                .with_context(asset_type="purchase")
                .create(
                    {
                        "account_depreciation_id": account_depreciation.id,
                        "account_depreciation_expense_id": account_asset_depreciation_expense.id,
                        "account_asset_id": account_asset.id,
                        "journal_id": journal.id,
                        "salvage_value": 2000.0,
                        "state": "open",
                        "method_period": "12",
                        "method_number": 5,
                        "name": "CEO's Car",
                        "original_value": 12000.0,
                    }
                )
            )
            asset.validate()
            asset2 = (
                self.env["account.asset"]
                .with_context(asset_type="purchase")
                .create(
                    {
                        "account_depreciation_id": account_depreciation.id,
                        "account_depreciation_expense_id": account_asset_depreciation_expense.id,
                        "account_asset_id": account_asset.id,
                        "journal_id": journal.id,
                        "salvage_value": 2000.0,
                        "state": "open",
                        "method_period": "12",
                        "method_number": 5,
                        "name": "CEO's Car",
                        "original_value": 12000.0,
                    }
                )
            )
            asset2.validate()

        return {
            "assets": [asset.id, asset2.id],
        }

    def check(self, init):
        for asset in self.env["account.asset"].browse(init["assets"]):
            moves = asset.depreciation_move_ids.sorted(lambda m: m.id)
            for i, depreciation_move in enumerate(moves):
                with self.subTest(depreciation_move=depreciation_move, i=i):
                    self.assertEqual(
                        depreciation_move.asset_depreciation_beginning_date, fields.Date.from_string(f"202{i}-01-01")
                    )
                    self.assertEqual(depreciation_move.asset_number_days, 360)
                    self.assertEqual(depreciation_move.depreciation_value, 2000)
