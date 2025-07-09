from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "project.action_server_view_my_task")
    util.remove_field(cr, "report.project.task.user", "is_template")
    util.remove_view(cr, "project.view_task_template_search_form")
    util.remove_view(cr, "project.project_task_templates_kanban")
    util.remove_view(cr, "project.project_task_templates_list")
    util.remove_record(cr, "project.action_server_convert_to_template")
    util.remove_field(cr, "project.task", "has_project_template")
    util.remove_field(cr, "project.task", "has_template_ancestor")
    util.remove_field(cr, "project.task", "is_template", drop_column=False)
