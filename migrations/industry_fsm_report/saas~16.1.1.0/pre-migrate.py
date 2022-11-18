from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "industry_fsm_report.report_project_task_user_fsm_view_search")
    util.remove_view(cr, "industry_fsm_report.project_sharing_project_task_inherit_view_tree")
    util.remove_view(cr, "industry_fsm_report.project_sharing_quick_create_task_form_inherit")
    util.remove_view(cr, "industry_fsm_report.project_sharing_project_task_inherit_view_kanban")
    util.remove_view(cr, "industry_fsm_report.project_sharing_project_task_inherit_view_form")
    util.remove_view(cr, "industry_fsm_report.view_project_project_filter_inherit_industry_fsm_report")
    util.remove_view(cr, "industry_fsm_report.project_view_tree_primary")
    util.remove_view(cr, "industry_fsm_report.project_project_view_tree")
