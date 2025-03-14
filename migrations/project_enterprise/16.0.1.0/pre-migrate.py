from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "industry_fsm.project_task_view_gantt_fsm")
