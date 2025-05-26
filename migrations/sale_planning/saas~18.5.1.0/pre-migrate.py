from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_planning.resource_sale_planning")
