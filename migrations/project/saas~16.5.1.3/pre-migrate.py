from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "project.project", "alias_enabled")
    util.remove_field(cr, "project.project", "alias_value")
    if not util.module_installed(cr, "industry_fsm"):
        cr.execute("DROP VIEW IF EXISTS report_project_task_user CASCADE")
        util.alter_column_type(cr, "project_task", "date_deadline", "timestamp without time zone", using="{0}")
    util.remove_field(cr, "res.company", "analytic_plan_id")
