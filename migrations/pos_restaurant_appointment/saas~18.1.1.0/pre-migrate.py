from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "pos_restaurant_appointment.calendar_event_view_form_gantt_booking_inherit")
    util.remove_view(cr, "pos_restaurant_appointment.calendar_event_view_gantt_booking_resource_inherited")
