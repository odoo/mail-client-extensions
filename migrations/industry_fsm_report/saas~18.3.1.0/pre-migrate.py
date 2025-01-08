from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "industry_fsm_report.project_task_gantt_view_groupby_worksheet2")
