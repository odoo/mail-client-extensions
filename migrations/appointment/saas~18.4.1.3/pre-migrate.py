from odoo.upgrade import util


def migrate(cr, version):
    util.remove_constraint(cr, "appointment_booking_line", "appointment_booking_line_check_capacity_used")
    util.remove_constraint(cr, "appointment_type", "appointment_type_check_resource_manual_confirmation_percentage")
    util.rename_field(cr, "appointment.type", "resource_manage_capacity", "manage_capacity")
    util.rename_field(
        cr, "appointment.type", "resource_manual_confirmation_percentage", "manual_confirmation_percentage"
    )
    util.rename_field(cr, "calendar.event", "resource_total_capacity_reserved", "total_capacity_reserved")
    util.rename_field(cr, "calendar.event", "resource_total_capacity_used", "total_capacity_used")

    cr.execute("ALTER TABLE appointment_booking_line ALTER COLUMN appointment_resource_id DROP NOT NULL")
    # Insert appointment booking lines for existing appointments with users.
    cr.execute(
        """
        INSERT INTO appointment_booking_line (
                    calendar_event_id, appointment_type_id, event_start, event_stop, capacity_reserved, capacity_used
                )
             SELECT ce.id, ce.appointment_type_id, ce.start, ce.stop, 1, 1
               FROM calendar_event ce
              WHERE user_id IS NOT NULL
                AND appointment_type_id IS NOT NULL
        """
    )
