from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "industry_fsm.project_task_action_fsm_map_view_activity")
    cr.execute(
        """
        DELETE FROM ir_act_window_view
              WHERE view_mode = 'activity'
                AND act_window_id IN %s
        """,
        [
            (
                util.ref(cr, "industry_fsm.project_task_action_fsm"),
                util.ref(cr, "industry_fsm.project_task_action_fsm_map"),
            )
        ],
    )
