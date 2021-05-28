# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util.accounting import no_fiscal_lock


@change_version("12.3")
class GroupedAssetsCase(UpgradeCase):
    def prepare(self):
        type_asset = self.env.ref("account.data_account_type_non_current_assets")
        type_depreciation = self.env.ref("account.data_account_type_depreciation")

        account_asset = self.env["account.account"].create(
            {"name": "_UPG_ Assets", "code": "241000", "user_type_id": type_asset.id}
        )
        account_depreciation = self.env["account.account"].create(
            {"name": "_UPG_ Assets Depreciation", "code": "241900", "user_type_id": type_asset.id}
        )
        account_depreciation_expense = self.env["account.account"].create(
            {"name": "_UPG_ Assets Expense", "code": "630200", "user_type_id": type_depreciation.id}
        )

        journal = self.env["account.journal"].create({"name": "Misc", "type": "general", "code": "UPG_M"})

        category_common_vals = {
            "journal_id": journal.id,
            "account_asset_id": account_asset.id,
            "account_depreciation_id": account_depreciation.id,
            "account_depreciation_expense_id": account_depreciation_expense.id,
        }

        categories = self.env["account.asset.category"].create(
            [
                {**category_common_vals, "name": "Computers", "group_entries": True},
                {**category_common_vals, "name": "Cars", "group_entries": True},
                {**category_common_vals, "name": "Misc", "group_entries": False, "open_asset": True},
            ]
        )
        category_1, category_2, category_3 = categories

        assets = self.env["account.asset.asset"].create(
            [
                {"name": "Laptop 1", "category_id": category_1.id, "value": 1000.33, "salvage_value": 100},
                {"name": "Laptop 2", "category_id": category_1.id, "value": 800.34, "salvage_value": 50},
                {"name": "Laptop 3", "category_id": category_1.id, "value": 500.67, "salvage_value": 20},
                {"name": "Car 1", "category_id": category_2.id, "value": 16543.97, "salvage_value": 980},
                {"name": "Car 2", "category_id": category_2.id, "value": 35004.34, "salvage_value": 2040},
                {"name": "Misc 1", "category_id": category_3.id, "value": 450},
                {"name": "Misc 2", "category_id": category_3.id, "value": 666},
            ]
        )
        assets.validate()

        with no_fiscal_lock(self.env.cr):
            self.env["account.asset.asset"].compute_generated_entries(datetime.today())
            moves = assets.mapped("depreciation_line_ids.move_id")
            self.assertEquals(len(moves), 4)  # 2 categories, 2 moves for grouped + 2 moves for 1 ungrouped category

            # Modify the first asset move on purpose, to handle a difference between the assets amount and the move amount
            # Leave the second asset untouched to check it doesn't create a remaining move
            move_group_1 = assets[0].mapped("depreciation_line_ids.move_id")
            move_group_1.journal_id.update_posted = True
            move_group_1.button_cancel()
            debit_line = move_group_1.line_ids.filtered(lambda l: l.debit)
            credit_line = move_group_1.line_ids.filtered(lambda l: l.credit)
            move_group_1.write({"line_ids": [(1, debit_line.id, {"debit": 480}), (1, credit_line.id, {"credit": 480})]})
            move_group_1.action_post()

        return (
            assets.ids,
            [(m.name, m.amount) for m in moves],
            [len(a.depreciation_line_ids) for a in assets],
            assets.mapped("entry_count"),
        )

    def check(self, init):
        asset_ids, moves, line_count, entry_count = init

        assets = self.env["account.asset"].browse(asset_ids)
        # The number of depreciation has not changed
        self.assertEquals([len(asset.depreciation_move_ids) for asset in assets], line_count)
        # The number of posted depreciation has not changed
        self.assertEquals(assets.mapped("depreciation_entries_count"), entry_count)

        # Check content of migration journal
        mig_journal = self.env["account.journal"].search(
            [
                ("code", "=", "UPGAS"),
                ("company_id", "=", assets[0].company_id.id),
                ("active", "=", False),
            ]
        )
        mig_moves = self.env["account.move"].search([("journal_id", "=", mig_journal.id)])
        # 2 grouped depreciations + the 5 details of it + the manual change
        # Unmodified/ungrouped moves are not in this journal
        self.assertEquals(len(mig_moves), 8)
        # balance is 0 per account
        balance_per_account = defaultdict(float)
        for line in mig_moves.mapped("line_ids"):
            balance_per_account[line.account_id] += line.balance
        for balance in balance_per_account.values():
            self.assertAlmostEquals(balance, 0)
