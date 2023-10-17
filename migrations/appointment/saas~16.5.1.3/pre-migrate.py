# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(cr, "appointment.type", "category", {"website": "recurring"})
    util.create_column(cr, "appointment_type", "event_videocall_source", "varchar")
    util.rename_xmlid(
        cr, "appointment.appointment_type_action_custom_and_anytime", "appointment.appointment_type_action_custom"
    )

    # calendar_event_id is now required
    cr.execute("DELETE FROM appointment_answer_input WHERE calendar_event_id IS NULL")
