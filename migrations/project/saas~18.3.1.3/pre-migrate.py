from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_act_window
           SET path=NULL
         WHERE id=%s
           AND path='my-tasks'
        """,
        [util.ref(cr, "project.action_view_my_task")],
    )

    util.remove_view(cr, "project.rating_rating_project_view_kanban")
