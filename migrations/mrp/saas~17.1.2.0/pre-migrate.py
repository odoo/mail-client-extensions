from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mrp.production", "show_serial_mass_produce")
