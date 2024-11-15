from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "whatsapp.template", "has_invalid_button_number")
