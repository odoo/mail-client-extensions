# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mrp.unbuild", "allowed_mo_ids")

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
