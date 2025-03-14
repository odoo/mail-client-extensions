from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "timesheets_past_days_encoding_limit")
    util.remove_field(cr, "res.company", "timesheets_past_days_encoding_limit")
    util.create_column(cr, "hr_employee", "last_validated_timesheet_date", "date")
    cr.execute(
        """
        WITH employee_last_validated_timesheet_date AS (
            SELECT employee_id,
                   MAX(A.date) as last_validated_timesheet_date
              FROM account_analytic_line A
             WHERE A.validated = true
               AND A.project_id IS NOT NULL
          GROUP BY employee_id
        )
        UPDATE hr_employee E
           SET last_validated_timesheet_date = I.last_validated_timesheet_date
          FROM employee_last_validated_timesheet_date I
         WHERE I.employee_id = E.id
    """
    )
    util.remove_view(cr, "timesheet_grid.timesheet_grid_pivot_view")
    util.remove_view(cr, "timesheet_grid.timesheet_grid_pivot_view_my")
