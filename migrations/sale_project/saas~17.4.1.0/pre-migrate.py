from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.order", "project_id")
