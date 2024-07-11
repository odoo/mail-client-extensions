from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "project.task", "so_analytic_account_id")
    util.explode_execute(
        cr,
        """
        UPDATE account_analytic_line aal
           SET timesheet_invoice_type = CASE timesheet_invoice_type
                 WHEN 'timesheet_revenues' THEN 'billable_time'
                 ELSE 'other_costs'
               END
         WHERE (    timesheet_invoice_type = 'timesheet_revenues'
                AND unit_amount <= 0)
            OR (    timesheet_invoice_type IN ('service_revenues', 'other_revenues')
                AND unit_amount < 0)
        """,
        table="account_analytic_line",
        alias="aal",
    )
