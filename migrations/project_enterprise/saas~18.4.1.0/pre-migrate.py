from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "project_enterprise.project_enterprise_task_view_activity")
    util.remove_view(cr, "project_enterprise.view_project_enterprise_task_pivot")
    util.remove_view(cr, "project_enterprise.view_project_enterprise_task_graph")

    util.remove_record(cr, "project_enterprise.project_task_graph_action_view")
