from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.order.template.option", "product_uom_category_id")
    util.remove_field(cr, "sale.order.template.line", "product_uom_category_id")
    util.remove_field(cr, "sale.order.option", "product_uom_category_id")
