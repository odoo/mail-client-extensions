from odoo.upgrade import util


def migrate(cr, version):
    for view in (
        "fsm_project_task_view_gantt2",
        "project_task_gantt_view_grouped_by_location2",
        "project_task_gantt_view_grouped_by_project_and_users2",
        "project_task_view_gantt_fsm2",
        "project_task_view_gantt_fsm",
    ):
        util.remove_view(cr, f"industry_fsm.{view}")
