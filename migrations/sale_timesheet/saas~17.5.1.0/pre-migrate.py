from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "project.task", "so_analytic_account_id")
