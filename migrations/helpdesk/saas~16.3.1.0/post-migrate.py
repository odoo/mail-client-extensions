# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
            SELECT 1
              FROM helpdesk_team team
             WHERE team.auto_assignment IS TRUE
             LIMIT 1
        """
    )
    if cr.rowcount:
        helpdesk_user_group = util.env(cr)["res.groups"].browse(util.ref(cr, "helpdesk.group_helpdesk_user"))
        helpdesk_user_group.write({"implied_ids": [(4, util.ref(cr, "helpdesk.group_auto_assignment"))]})
