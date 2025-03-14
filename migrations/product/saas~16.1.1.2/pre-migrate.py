from odoo.upgrade import util


def migrate(cr, version):
    util.update_field_usage(cr, "product.pricelist.item", "active", "pricelist_id.active")
    util.remove_field(cr, "product.pricelist.item", "active")
