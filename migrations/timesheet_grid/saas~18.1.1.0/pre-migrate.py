from odoo.upgrade import util


def migrate(cr, version):
    util.update_field_usage(cr, "account.analytic.line", "unit_amount_validate", "unit_amount")
    util.remove_field(cr, "account.analytic.line", "unit_amount_validate")
    util.update_field_usage(cr, "account.analytic.line", "duration_unit_amount", "unit_amount")
    util.remove_field(cr, "account.analytic.line", "duration_unit_amount")
