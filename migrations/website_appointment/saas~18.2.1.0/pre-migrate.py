from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "website_appointment.s_appointments_000_js")
    util.remove_record(cr, "website_appointment.s_searchbar_000_js")
