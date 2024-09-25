def migrate(cr, version):
    cr.execute("ALTER TABLE calendar_booking_line ALTER COLUMN appointment_resource_id DROP NOT NULL")
    cr.execute(
        """
            INSERT INTO calendar_booking_line (
                            calendar_booking_id, capacity_reserved, capacity_used
                        )
                 SELECT cb.id, 1, 1
                   FROM calendar_booking cb
                  WHERE staff_user_id IS NOT NULL
        """
    )
