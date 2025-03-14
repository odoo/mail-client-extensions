from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        """
            UPDATE project_task
               SET date_deadline = planned_date_end
             WHERE planned_date_end >= planned_date_begin
        """,
        table="project_task",
    )
    util.explode_execute(
        cr,
        """
            UPDATE project_task
               SET planned_date_begin = NULL
             WHERE planned_date_begin > date_deadline
        """,
        table="project_task",
    )

    util.update_field_usage(cr, "project.task", "planned_date_end", "date_deadline")
    util.update_field_usage(cr, "report.project.task.user", "planned_date_end", "date_deadline")
    util.remove_field(cr, "project.task", "planned_date_end")
    util.remove_field(cr, "report.project.task.user", "planned_date_end")
    util.remove_model(cr, "project.task.confirm.schedule.wizard")
    util.remove_model(cr, "project.task.confirm.schedule.line.wizard")
