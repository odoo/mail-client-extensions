from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.company", "expense_outstanding_account_id")
    util.remove_field(cr, "res.config.settings", "expense_outstanding_account_id")
