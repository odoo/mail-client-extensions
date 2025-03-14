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
    util.remove_field(cr, "pos.config", "is_table_management")
    util.remove_field(cr, "res.config.settings", "pos_is_table_management")
