from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "appointment_hr.calendar_event_view_form_gantt_booking_inherit_appointment_hr")
