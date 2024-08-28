from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(
        cr,
        "pos.order.line",
        "note",
        "pos_restaurant",
        "point_of_sale",
    )
