from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_attendance.hr_attendance_validated_hours_employee_simple_tree_view")
    util.remove_view(cr, "hr_attendance.hr_user_view_form")

    util.remove_field(cr, "res.users", "attendance_state")
    util.remove_field(cr, "res.users", "attendance_state")
    util.remove_field(cr, "res.users", "last_check_in")
    util.remove_field(cr, "res.users", "last_check_out")
    util.remove_field(cr, "res.users", "hours_last_month")
    util.remove_field(cr, "res.users", "hours_last_month_display")
    util.remove_field(cr, "res.users", "total_overtime")
    util.remove_field(cr, "res.users", "hours_last_month_overtime")
    util.remove_field(cr, "res.users", "attendance_manager_id")
    util.remove_field(cr, "res.users", "display_extra_hours")

    util.remove_field(cr, "hr.attendance", "no_validated_overtime_hours")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("hr_attendance.view_attendance_overtime_{tree,list}"))

    util.create_column(cr, "hr_attendance", "date", "date")
    util.explode_execute(
        cr,
        """
        UPDATE hr_attendance
           SET "date" = date(check_in)
        """,
        table="hr_attendance",
    )

    cr.execute("""
        CREATE TABLE hr_attendance_overtime_line (
            id SERIAL PRIMARY KEY,
            create_uid integer,
            create_date timestamp without time zone,
            write_uid integer,
            write_date timestamp without time zone,
            employee_id integer NOT NULL,
            "date" date NOT NULL,
            status varchar NOT NULL,
            duration double precision NOT NULL,
            manual_duration double precision,
            time_start timestamp without time zone,
            time_stop timestamp without time zone,
            amount_rate double precision NOT NULL
        );
        CREATE INDEX hr_attendance_overtime_line_employee_idx ON hr_attendance_overtime_line (employee_id);
        CREATE INDEX hr_attendance_overtime_line_date_idx ON hr_attendance_overtime_line (date);
    """)

    cr.execute("""
        INSERT INTO hr_attendance_overtime_line (
            employee_id,
            "date",
            status,
            duration,
            manual_duration,
            amount_rate
        )
        SELECT
            employee_id,
            "date",
            overtime_status,
            SUM(overtime_hours) AS duration,
            SUM(validated_overtime_hours) AS manual_duration,
            1.0 AS amount_rate   -- default value, since required
        FROM hr_attendance
        WHERE overtime_hours > 0 OR validated_overtime_hours > 0
        GROUP BY employee_id, "date", overtime_status;
    """)

    util.remove_model(cr, "hr.attendance.overtime")
