from odoo.upgrade import util


def migrate(cr, version):
    if version.startswith("saas~17.4."):
        util.create_column(cr, "hr_employee", "billable_time_target", "float8")
        cr.execute("""
            SELECT he.id, CEIL(rc.hours_per_day * 20 * he.billing_rate_target) AS target
                FROM hr_employee he
                JOIN resource_calendar rc
                ON he.resource_calendar_id = rc.id
            WHERE he.billing_rate_target IS NOT NULL
        """)
        data = cr.fetchall()
        for employee_id, target in data:
            cr.execute(
                "UPDATE hr_employee he SET billable_time_target = %s WHERE id = %s",
                [
                    target,
                    employee_id,
                ],
            )
        util.remove_field(cr, "hr.employee", "billing_rate_target")
        util.rename_field(cr, "hr.employee", "show_billing_rate_target", "show_billable_time_target")
        util.remove_constraint(cr, "hr_employee", "hr_employee_check_billable_rate_target")
