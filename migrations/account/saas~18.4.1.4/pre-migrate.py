from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(
        cr,
        "account.reconcile.model.line",
        "amount_type",
        {"from_transaction_details": "regex"},
    )
