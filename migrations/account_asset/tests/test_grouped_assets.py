# -*- coding: utf-8 -*-
from datetime import datetime

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import change_version, UpgradeCase
from odoo.tools import float_compare


@change_version("12.3")
class GroupedAssetsCase(UpgradeCase):
    def prepare(self):

        if util.version_gte("saas~12.4"):
            amount_col = "amount_total"
        else:
            amount_col = "amount"

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
            "group_entries": True,
        }

        category_1 = self.env["account.asset.category"].create(dict(category_common_vals, name="Computers"))
        category_2 = self.env["account.asset.category"].create(dict(category_common_vals, name="Cars"))

        asset_1 = self.env["account.asset.asset"].create(
            {"name": "Laptop 1", "category_id": category_1.id, "value": 1000.33, "salvage_value": 100}
        )
        asset_2 = self.env["account.asset.asset"].create(
            {"name": "Laptop 2", "category_id": category_1.id, "value": 800.34, "salvage_value": 50}
        )
        asset_3 = self.env["account.asset.asset"].create(
            {"name": "Laptop 3", "category_id": category_1.id, "value": 500.67, "salvage_value": 20}
        )
        asset_4 = self.env["account.asset.asset"].create(
            {"name": "Car 1", "category_id": category_2.id, "value": 16543.97, "salvage_value": 980}
        )
        asset_5 = self.env["account.asset.asset"].create(
            {"name": "Car 2", "category_id": category_2.id, "value": 35004.34, "salvage_value": 2040}
        )

        assets = asset_1 + asset_2 + asset_3 + asset_4 + asset_5
        assets.validate()
        self.env["account.asset.asset"].compute_generated_entries(datetime.today())
        moves = assets.mapped("depreciation_line_ids.move_id")
        self.assertEquals(len(moves), 2)  # 2 categories, 2 moves

        # Modify the first asset move on purpose, to handle a difference between the assets amount and the move amount
        # Leave the second asset untouched to check it doesn't create a remaining move
        move_group_1 = asset_1.mapped("depreciation_line_ids.move_id")
        move_group_1.journal_id.update_posted = True
        move_group_1.button_cancel()
        debit_line = move_group_1.line_ids.filtered(lambda l: l.debit)
        credit_line = move_group_1.line_ids.filtered(lambda l: l.credit)
        move_group_1.write({"line_ids": [(1, debit_line.id, {"debit": 480}), (1, credit_line.id, {"credit": 480})]})
        move_group_1.action_post()

        return (
            assets.ids,
            [(m.name, m[amount_col]) for m in moves],
            [len(a.depreciation_line_ids) for a in assets],
            assets.mapped("entry_count"),
        )

    def check(self, init):
        asset_ids, moves, line_count, entry_count = init

        if util.version_gte("saas~12.4"):
            amount_col = "amount_total"
        else:
            amount_col = "amount"

        assets = self.env["account.asset"].browse(asset_ids)
        # 4 moves are expected for the first grouped move: 3 depreciation lines + 1 remaining,
        # as the move was edited manually.
        # 2 moves are expected for the second grouped move: 2 depreciation lines.
        expected_move_count = [4, 2]
        for (name, amount), move_count in zip(moves, expected_move_count):
            moves = self.env["account.move"].search([("name", "=like", name + "/%")], order="name")
            self.assertTrue(float_compare(sum(moves.mapped(amount_col)), amount, precision_rounding=2) == 0)
            self.assertEquals(len(moves), move_count)
            for i, move in enumerate(moves, start=1):
                self.assertTrue(move.name.endswith("/%s" % i))
        self.assertEquals([len(asset.depreciation_move_ids) for asset in assets], line_count)
        self.assertEquals(assets.mapped("depreciation_entries_count"), entry_count)
