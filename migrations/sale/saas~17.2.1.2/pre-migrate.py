from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.analytic.line", "allowed_so_line_ids")
