from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.company", "expense_outstanding_account_id")
    util.remove_field(cr, "res.config.settings", "expense_outstanding_account_id")
    util.remove_field(cr, "res.users", "expense_manager_id")

    util.remove_view(cr, "hr_expense.res_users_view_form_preferences")
