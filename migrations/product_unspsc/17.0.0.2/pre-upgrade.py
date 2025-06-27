from odoo.upgrade import util


def migrate(cr, version):
    util.convert_field_to_translatable(cr, "product.unspsc.code", "name")
