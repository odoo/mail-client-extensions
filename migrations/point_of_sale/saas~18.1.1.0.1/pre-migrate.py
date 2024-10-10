from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "pos.session", "login_number")
    util.remove_field(cr, "pos.session", "sequence_number")
