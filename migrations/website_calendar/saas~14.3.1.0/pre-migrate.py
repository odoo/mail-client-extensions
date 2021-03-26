# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "calendar_appointment_type", "cover_properties", "text")
    background = """{
        'background-image': 'url("/website_calendar/static/src/img/appointment_cover_0.jpg")',
        'resize_class': 'o_record_has_cover o_half_screen_height',
        'opacity': '0.4'
    }"""
    cr.execute(
        """
            UPDATE calendar_appointment_type
            SET cover_properties = %s
        """,
        (background,),
    )
    util.create_column(cr, "calendar_appointment_slot", "end_hour", "float8")
    cr.execute(
        """
            UPDATE calendar_appointment_slot slot
            SET end_hour = slot.hour + t.appointment_duration
            FROM calendar_appointment_type t
            WHERE t.id = slot.appointment_type_id
        """
    )
    util.remove_view(cr, "website_calendar.appointment")
    util.remove_view(cr, "website_calendar.index")
    util.remove_view(cr, "website_calendar.setup")
    util.rename_field(cr, "calendar.appointment.type", "assignation_method", "assign_method")
    util.rename_field(cr, "calendar.appointment.slot", "hour", "start_hour")
