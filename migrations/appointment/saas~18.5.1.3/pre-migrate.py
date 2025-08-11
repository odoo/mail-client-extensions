from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "appointment.invite", "has_identical_config")
    util.remove_menus(cr, [util.ref(cr, "appointment.menu_schedule_report_all_events")])

    util.remove_menus(cr, [util.ref(cr, "appointment.menu_appointment_type_custom")])
    util.remove_record(cr, "appointment.appointment_type_action_custom")
    util.remove_record(cr, "appointment.appointment_type_view_tree_invitation")

    cr.execute("""
        DELETE FROM appointment_slot
              WHERE slot_type = 'unique'
                AND ((start_datetime IS NULL OR end_datetime IS NULL) OR
                     (start_datetime > end_datetime)
                    )
    """)
