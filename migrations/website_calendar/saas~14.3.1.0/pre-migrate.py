# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    module = "website_appointment" if util.version_gte("saas~14.5") else "website_calendar"
    background = f"""{{
        "background-image": "url(/{module}/static/src/img/appointment_cover_0.jpg)",
        "resize_class": "o_record_has_cover o_half_screen_height",
        "opacity": "0.4"
    }}"""
    util.create_column(cr, "calendar_appointment_type", "cover_properties", "text", default=background)

    util.create_column(cr, "calendar_appointment_slot", "end_hour", "float8")
    cr.execute(
        """
            UPDATE calendar_appointment_slot slot
            SET end_hour = slot.hour + t.appointment_duration
            FROM calendar_appointment_type t
            WHERE t.id = slot.appointment_type_id
        """
    )
    module = "appointment" if util.version_gte("saas~14.5") else "website_calendar"
    util.remove_view(cr, f"{module}.appointment")
    util.remove_view(cr, f"{module}.index")
    util.remove_view(cr, f"{module}.setup")
    util.rename_field(cr, "calendar.appointment.type", "assignation_method", "assign_method")
    util.rename_field(cr, "calendar.appointment.slot", "hour", "start_hour")
