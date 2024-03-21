from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("ALTER TABLE employee_category_rel RENAME COLUMN emp_id TO employee_id")

    util.remove_record(cr, "hr.act_employee_from_department")
    remove_fields = [
        "module_hr_attendance",
        "hr_presence_control_ip",
        "hr_presence_control_login",
        "hr_presence_control_email",
    ]
    for field in remove_fields:
        util.remove_column(cr, "res_config_settings", field)

    util.create_column(cr, "hr_employee", "is_flexible", "boolean", default=False)
    util.create_column(cr, "hr_employee", "is_fully_flexible", "boolean", default=False)

    # Populate the field is_flexible by finding the employees whose resource_calendar
    # had flexible_hours set to True.
    query = util.format_query(
        cr,
        """
        WITH flexible_employees AS (
          SELECT e.id,
                 c.flexible_hours
            FROM hr_employee e
            JOIN resource_resource r ON e.resource_id = r.id
            JOIN resource_calendar c ON r.calendar_id = c.id
           WHERE c.flexible_hours = True
        )
        UPDATE hr_employee e
           SET is_flexible = True
          FROM flexible_employees fe
         WHERE e.id = fe.id
        """,
    )
    cr.execute(query)
