from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "appointment.type", "user_assign_method")
