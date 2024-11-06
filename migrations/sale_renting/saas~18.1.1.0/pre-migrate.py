from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "sale.rental.report", "product_uom", "product_uom_id")
    util.rename_field(cr, "sale.rental.schedule", "product_uom", "product_uom_id")
