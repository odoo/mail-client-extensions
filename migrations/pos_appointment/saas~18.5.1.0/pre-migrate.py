from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr,
        "pos_appointment.calendar_event_view_form_gantt_booking_inherited_pos_appointment",
        "pos_appointment.calendar_event_view_form_gantt_booking",
    )
    util.rename_xmlid(
        cr,
        "pos_appointment.calendar_event_view_gantt_booking_resource_inherited_pos_appointment",
        "pos_appointment.calendar_event_view_gantt_booking_resource",
    )
    util.rename_xmlid(
        cr,
        "pos_appointment.calendar_event_view_tree_inherited_restaurant_appointment",
        "pos_appointment.calendar_event_view_tree",
    )
    util.rename_xmlid(
        cr,
        "pos_appointment.calendar_event_view_kanban_pos_restaurant_appointment",
        "pos_appointment.calendar_event_view_kanban",
    )
