from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "res.config.settings", "use_mailgateway", "hr_expense_use_mailgateway")
    util.rename_field(cr, "res.config.settings", "expense_alias_prefix", "hr_expense_alias_prefix")
