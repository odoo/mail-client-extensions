from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "website_appointment.s_online_appointment_000_js")
