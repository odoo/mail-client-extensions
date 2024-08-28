from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "appointment.type", "appointment_count_report")
