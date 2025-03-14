from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_disallowed_expenses.disallowed_expenses_main_template")
