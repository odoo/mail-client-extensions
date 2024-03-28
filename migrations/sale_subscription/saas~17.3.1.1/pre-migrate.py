from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.order", "archived_product_ids")
    util.remove_field(cr, "sale.order", "archived_product_count")
