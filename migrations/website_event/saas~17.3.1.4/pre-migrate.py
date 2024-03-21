from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "event.type", "menu_register_cta")
    util.remove_field(cr, "event.event", "menu_register_cta")
