# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mrp.unbuild", "allowed_mo_ids")
    util.remove_field(cr, "mrp.production", "confirm_no_consumption")

    util.rename_field(cr, "res.config.settings", "group_locked_by_default", "group_unlocked_by_default")
    util.rename_xmlid(cr, "mrp.group_locked_by_default", "mrp.group_unlocked_by_default")

    # we're renaming an implied group setting + the group's ID, but reversing its purpose =>
    # need to record the opposite of the previous setting
    usr_id = util.ref(cr, "base.group_user")
    xml_id = util.ref(cr, "mrp.group_unlocked_by_default")
    cr.execute(
        """
            DELETE
              FROM res_groups_users_rel
             WHERE gid=%s
        """,
        [xml_id],
    )
    cr.execute(
        """
            DELETE
              FROM res_groups_implied_rel
             WHERE gid=%s
               AND hid=%s
        """,
        [usr_id, xml_id],
    )
    if not cr.rowcount:
        cr.execute(
            """
                INSERT INTO res_groups_implied_rel (gid, hid)
                     VALUES(%s, %s)
            """,
            [usr_id, xml_id],
        )
        util.env(cr)["res.groups"].browse(usr_id).write({"implied_ids": [(4, xml_id)]})

    util.create_column(cr, "mrp_workorder", "costs_hour", "float8")

    cr.execute(
        """
            UPDATE mrp_workorder AS wo
               SET costs_hour = wc.costs_hour
              FROM mrp_workcenter_productivity p
              JOIN mrp_workcenter wc ON wc.id = p.workcenter_id
             WHERE wo.id = p.workorder_id
               AND wo.state = 'done'
        """
    )

    util.create_column(cr, "stock_move", "cost_share", "numeric", default=0)
    util.create_column(cr, "mrp_bom_byproduct", "cost_share", "numeric", default=0)
