from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "industry_fsm_report.project_sharing_project_task_view_search")
