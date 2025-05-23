from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.journal", "autocheck_on_post")
    util.change_field_selection_values(
        cr,
        "account.reconcile.model.line",
        "amount_type",
        {"from_transaction_details": "regex"},
    )
