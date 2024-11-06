from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "product.supplierinfo", "product_uom", "product_uom_id")
    util.rename_field(cr, "product.pricelist.item", "product_uom", "product_uom_name")
