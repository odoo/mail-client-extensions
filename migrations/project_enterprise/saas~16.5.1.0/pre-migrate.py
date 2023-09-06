# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        """
        UPDATE project_task
            SET date_deadline = CASE
                    WHEN planned_date_end >= planned_date_begin THEN planned_date_end
                    WHEN date_deadline >= planned_date_begin THEN date_deadline
                    ELSE null
                END,
                planned_date_begin = CASE
                    WHEN planned_date_end >= planned_date_begin THEN planned_date_begin
                    WHEN date_deadline >= planned_date_begin THEN planned_date_begin
                    ELSE null
                END
        """,
        table="project_task",
    )

    util.update_field_usage(cr, "project.task", "planned_date_end", "date_deadline")
    util.update_field_usage(cr, "report.project.task.user", "planned_date_end", "date_deadline")
    util.remove_field(cr, "project.task", "planned_date_end")
    util.remove_field(cr, "report.project.task.user", "planned_date_end")
    util.remove_model(cr, "project.task.confirm.schedule.wizard")
    util.remove_model(cr, "project.task.confirm.schedule.line.wizard")
