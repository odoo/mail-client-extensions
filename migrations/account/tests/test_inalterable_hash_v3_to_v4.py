from odoo import fields
from odoo.tools import format_date

from odoo.addons.base.maintenance.migrations.account.tests.test_common import TestAccountingSetupCommon
from odoo.addons.base.maintenance.migrations.testing import change_version
from odoo.addons.base.maintenance.migrations.util.accounting import no_fiscal_lock


@change_version("saas~17.2")
class TestAccountMoveInalterableHashV3ToV4Upgrade(TestAccountingSetupCommon):
    def _prepare_invoices(self, dates, account_id, partner_id):
        return self.env["account.move"].create(
            [
                {
                    "move_type": "out_invoice",
                    "partner_id": partner_id,
                    "invoice_date": fields.Date.from_string(date),
                    "invoice_line_ids": [
                        fields.Command.create(
                            {
                                "name": "Product",
                                "quantity": 1,
                                "price_unit": 100,
                                "account_id": account_id,
                            },
                        )
                    ],
                }
                for date in dates
            ]
        )

    def prepare(self):
        res = super().prepare()
        dates = ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
        account_id = res["config"]["account_receivable_id"]
        partner_id = res["config"]["partner_id"]
        with no_fiscal_lock(self.env.cr):
            moves = self._prepare_invoices(dates, account_id, partner_id)
            moves[0].journal_id.restrict_mode_hash_table = True
            moves.action_post()
        res["tests"].append(("_check_inalterable_hash", [moves.ids]))
        return res

    def _check_inalterable_hash(self, config, move_ids):
        self.env.company = self.env["res.company"].browse(config["company_id"])
        moves = self.env["account.move"].browse(move_ids)
        account_id = config["account_receivable_id"]
        partner_id = config["partner_id"]
        moves.env.user.groups_id |= self.env.ref("account.group_account_user")

        # Check that the hashing chain check is still correct after the upgrade
        integrity_check = moves.company_id._check_hash_integrity()["results"]
        result = next(filter(lambda r: moves.journal_id.name in r.get("journal_name"), integrity_check))
        self.assertEqual(result["status"], "verified")
        self.assertEqual(result["first_move_date"], format_date(self.env, fields.Date.to_string(moves[0].date)))
        self.assertEqual(result["last_move_date"], format_date(self.env, fields.Date.to_string(moves[-1].date)))

        with no_fiscal_lock(self.env.cr):
            new_moves = self._prepare_invoices(["2024-01-06", "2024-01-07"], account_id, partner_id)
            moves |= new_moves
            new_moves.action_post()
            new_moves.button_hash()

        # Check that the hashing chain check is still correct after adding new moves
        integrity_check = moves.company_id._check_hash_integrity()["results"]
        result = next(filter(lambda r: moves.journal_id.name in r.get("journal_name"), integrity_check))
        self.assertEqual(result["status"], "verified")
        self.assertEqual(result["first_move_date"], format_date(self.env, fields.Date.to_string(moves[0].date)))
        self.assertEqual(result["last_move_date"], format_date(self.env, fields.Date.to_string(moves[-1].date)))
