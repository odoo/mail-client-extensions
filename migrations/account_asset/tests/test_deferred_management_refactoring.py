# -*- coding: utf-8 -*-

from freezegun import freeze_time

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

REF_DATE = "2023-01-01"


@change_version("saas~16.3")
class AccountAssetDeferredManagementUpgrade(UpgradeCase):
    def create_asset(
        self, name, asset_type, account_depreciation, account_asset_depreciation_expense, account_asset, journal
    ):
        asset = (
            self.env["account.asset"]
            .with_context(asset_type=asset_type)
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
                    "name": name,
                    "original_value": 12000.0,
                }
            )
        )
        asset.validate()
        return asset

    def prepare(self):
        with freeze_time(REF_DATE):
            account_asset, account_asset_depreciation_expense, account_depreciation = self.env[
                "account.account"
            ].create(
                [
                    {
                        "name": "Fixed Assets",
                        "account_type": "asset_fixed",
                        "code": "123",
                    },
                    {
                        "name": "Expenses",
                        "code": "456",
                        "account_type": "expense",
                    },
                    {
                        "name": "_UPG_ assets depreciation expense",
                        "code": "789",
                        "account_type": "asset_current",
                    },
                ]
            )
            journal = self.env["account.journal"].create(
                {"name": "_UPG_ miscellaneous", "type": "general", "code": "UPG_M"}
            )
            asset = self.create_asset(
                "TO KEEP", "purchase", account_depreciation, account_asset_depreciation_expense, account_asset, journal
            )
            deferred_revenue = self.create_asset(
                "TO DELETE", "sale", account_depreciation, account_asset_depreciation_expense, account_asset, journal
            )
            deferred_expense = self.create_asset(
                "TO DELETE", "expense", account_depreciation, account_asset_depreciation_expense, account_asset, journal
            )

        return {
            "asset": asset.id,
            "asset_moves": asset.depreciation_move_ids.ids,
            "deferred_revenue": deferred_revenue.id,
            "deferred_revenue_moves": deferred_revenue.depreciation_move_ids.ids,
            "deferred_expense": deferred_expense.id,
            "deferred_expense_moves": deferred_expense.depreciation_move_ids.ids,
        }

    def check(self, init):
        # Account asset and its depreciation moves should still exist
        asset = self.env["account.asset"].browse(init["asset"])
        asset_moves = self.env["account.move"].browse(init["asset_moves"])
        self.assertEqual(sorted(asset.depreciation_move_ids.ids), sorted(asset_moves.ids))

        # Deferred revenue/expense should not exist anymore
        self.assertEqual(self.env["account.asset"].search_count([("id", "=", init["deferred_revenue"])]), 0)
        self.assertEqual(self.env["account.asset"].search_count([("id", "=", init["deferred_expense"])]), 0)

        # However, their depreciation moves should still exist
        self.assertEqual(
            self.env["account.move"].search_count([("id", "in", init["deferred_revenue_moves"])]),
            len(init["deferred_revenue_moves"]),
        )
        self.assertEqual(
            self.env["account.move"].search_count([("id", "in", init["deferred_expense_moves"])]),
            len(init["deferred_expense_moves"]),
        )

        #  No asset 'deferred revenue/expense'
        self.assertEqual(self.env["account.asset"].search_count([("name", "=", "TO DELETE")]), 0)
        self.assertEqual(self.env["account.asset"].search_count([("name", "=", "TO KEEP")]), 1)
