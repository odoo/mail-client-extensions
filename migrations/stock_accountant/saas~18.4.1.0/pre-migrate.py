from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "property_account_expense_categ_id")
    util.remove_field(cr, "res.config.settings", "property_account_income_categ_id")
