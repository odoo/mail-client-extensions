from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "batch_payroll_move_lines", "boolean", default=True)
