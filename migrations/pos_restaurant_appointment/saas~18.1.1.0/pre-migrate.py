from odoo.upgrade import util


def migrate(cr, version):
    module = "pos_appointment" if util.version_gte("saas~18.3") else "pos_restaurant_appointment"
    util.remove_view(cr, f"{module}.calendar_event_view_form_gantt_booking_inherit")
    util.remove_view(cr, f"{module}.calendar_event_view_gantt_booking_resource_inherited")
