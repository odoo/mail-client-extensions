from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    if util.column_exists(cr, "project_task", "allocated_hours"):
        # in versions < saas~16.2, the field `allocated_hours` was a compute-stored field added by the `project_enterprise` moduled. We can just remove it.
        util.remove_field(cr, "project.task", "allocated_hours")
        util.remove_field(cr, "report.project.task.user", "allocated_hours")
    util.rename_field(cr, "project.task", "planned_hours", "allocated_hours")
    util.rename_field(cr, "project.task", "subtask_planned_hours", "subtask_allocated_hours")
    util.rename_field(cr, "project.task.burndown.chart.report", "planned_hours", "allocated_hours")
    util.rename_xmlid(cr, *eb("project.portal_my_task_{planned,allocated}_hours_template"))
