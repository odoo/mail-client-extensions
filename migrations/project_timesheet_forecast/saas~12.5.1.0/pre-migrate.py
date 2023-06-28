# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "planning_slot", "effective_hours", "float8")
    util.create_column(cr, "planning_slot", "percentage_hours", "float8")

    cr.execute("""
        UPDATE planning_slot
           SET percentage_hours = CASE WHEN allocated_hours!=0 THEN effective_hours / allocated_hours ELSE 0 END
    """)

    util.explode_execute(
        cr,
        """
        UPDATE planning_slot
            SET effective_hours=timesheets.effective_hours
            FROM (SELECT ps.id,timesheet.effective_hours
                FROM planning_slot ps
        JOIN LATERAL (
                    SELECT sum(unit_amount) as effective_hours
                    FROM account_analytic_line ts
                    WHERE ts.user_id=ps.user_id
                        AND ts.date>=ps.start_datetime::date
                        AND ts.date<=ps.end_datetime::date
                        AND (   (ps.task_id=ts.task_id)
                            OR (ps.task_id IS NULL AND ps.project_id=ts.project_id)
                            OR (ps.task_id IS NULL AND ps.project_id IS NULL)
                            )
                ) as timesheet ON TRUE) as timesheets
            WHERE timesheets.id=planning_slot.id
        """,
        table="planning_slot",
    )

    util.rename_field(cr, "project.timesheet.forecast.report.analysis", "date", "entry_date")
