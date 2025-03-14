from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_model(cr, "account.disallowed.expenses.report")
    util.remove_view(cr, "account_disallowed_expenses.main_template_de")
