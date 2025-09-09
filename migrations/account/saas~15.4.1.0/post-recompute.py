from odoo.upgrade import util


def migrate(cr, version):
    query = "SELECT id FROM account_move WHERE state IN ('draft', 'cancel')"
    util.recompute_fields(
        cr, "account.move", ["amount_residual", "amount_residual_signed"], query=query, strategy="commit"
    )
