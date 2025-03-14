from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "project.task", "allow_billable", "sale_timesheet", "sale_project")
    util.remove_view(cr, "sale_project.project_sharing_inherit_project_task_view_search")
    util.remove_view(cr, "sale_project.view_task_project_user_search_inherited")
