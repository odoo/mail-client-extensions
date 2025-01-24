from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "hr_attendance.open_kiosk_url")
    util.remove_menus(cr, [util.ref(cr, "hr_attendance.menu_hr_attendance_kiosk_no_user_mode")])

    util.create_column(cr, "res_company", "attendance_overtime_validation", "varchar")
    cr.execute(
        """
        UPDATE res_company SET attendance_overtime_validation = CASE WHEN hr_attendance_overtime IS True
                                                                     THEN 'no_validation'
                                                                     ELSE 'by_manager'
                                                                     END
        """
    )

    util.create_column(cr, "hr_attendance", "overtime_status", "varchar")
    util.create_column(cr, "hr_attendance", "validated_overtime_hours", "float8")

    util.explode_execute(
        cr,
        """
        UPDATE hr_attendance a
           SET overtime_status = CASE
                WHEN (c.hr_attendance_overtime IS TRUE AND a.check_in > c.overtime_start_date) THEN 'approved'
                ELSE 'refused'
               END -- validated_overtime_hours compute moves in post
        FROM hr_employee e
        JOIN res_company c
          ON c.id = e.company_id
        WHERE e.id = a.employee_id
        """,
        table="hr_attendance",
        alias="a",
    )

    util.remove_field(cr, "res.company", "hr_attendance_overtime")
    util.remove_field(cr, "res.company", "overtime_start_date")
    util.remove_field(cr, "res.config.settings", "hr_attendance_overtime")
    util.remove_field(cr, "res.config.settings", "overtime_start_date")
