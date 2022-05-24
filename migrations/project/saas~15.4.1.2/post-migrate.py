# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    fsm = ""
    if util.column_exists(cr, "project_project", "is_fsm"):
        # don't allow milestones on FSM projects, even if defined
        fsm = "AND NOT p.is_fsm"
    cr.execute(
        f"""
        UPDATE project_project p
           SET allow_milestones = true
          FROM project_milestone m
         WHERE m.project_id = p.id
         {fsm}
        """
    )
    if cr.rowcount:
        env = util.env(cr)
        internal_user_group = env.ref("base.group_user")
        internal_user_group.write(
            {
                "implied_ids": [(4, util.ref(cr, "project.group_project_milestone"))],
            }
        )
