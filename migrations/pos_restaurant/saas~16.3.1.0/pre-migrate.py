# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "pos.order", "multiprint_resume")
    util.remove_field(cr, "pos.order.line", "mp_skip")
    util.remove_menus(
        cr,
        [
            util.ref(cr, "pos_restaurant.menu_restaurant_printer_all"),
        ],
    )
