from odoo.upgrade import util


def migrate(cr, version):
    util.make_field_non_stored(cr, "product.template", "self_order_visible", selectable=False)
