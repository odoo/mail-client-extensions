# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "helpdesk.ticket", "commercial_partner_id", "helpdesk_sale", "helpdesk")
    util.remove_field(cr, "helpdesk.ticket", "is_self_assigned")

    helpdesk_user_group_id = util.ref(cr, "helpdesk.group_helpdesk_user")
    # add users from visibility_member_ids if member_ids is empty.
    cr.execute(
        """
            INSERT INTO helpdesk_team_res_users_rel(helpdesk_team_id, res_users_id)
            SELECT vt.helpdesk_team_id, vt.res_users_id
              FROM helpdesk_visibility_team vt
              JOIN helpdesk_team ht ON ht.id = vt.helpdesk_team_id
              JOIN res_company_users_rel rc ON rc.cid = ht.company_id AND rc.user_id = vt.res_users_id
              JOIN res_groups_users_rel rg ON rg.uid = vt.res_users_id AND rg.gid = %s
             WHERE ht.id NOT IN (SELECT helpdesk_team_id FROM helpdesk_team_res_users_rel GROUP BY helpdesk_team_id)

        """,
        [helpdesk_user_group_id],
    )
    # Add all users from the group 'helpdesk.group_helpdesk_user' for the team without access
    cr.execute(
        """
            INSERT INTO helpdesk_team_res_users_rel(helpdesk_team_id, res_users_id)
            SELECT ht.id, rg.uid
              FROM helpdesk_team ht
              JOIN res_groups_users_rel rg ON rg.gid = %s
              JOIN res_company_users_rel rc ON rc.cid = ht.company_id AND rc.user_id = rg.uid
             WHERE ht.id NOT IN (SELECT helpdesk_team_id FROM helpdesk_team_res_users_rel GROUP BY helpdesk_team_id)
        """,
        [helpdesk_user_group_id],
    )
