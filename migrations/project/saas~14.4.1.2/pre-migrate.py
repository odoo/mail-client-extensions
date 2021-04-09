# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # add project allowed internal users to mail followers if absent for project with followers.
    # add project allowed portal users to mail followers if absent for project portal.
    # reverts migration 13.2.1.1
    cr.execute(
        """
        INSERT INTO mail_followers(res_model, res_id, partner_id)
             SELECT 'project.project', p.id, u.partner_id
               FROM project_project p
               JOIN project_allowed_internal_users_rel a ON a.project_project_id = p.id
               JOIN res_users u ON u.id = a.res_users_id
              WHERE p.privacy_visibility = 'followers'
                AND u.share = false
        ON CONFLICT DO NOTHING
    """
    )
    cr.execute(
        """
        INSERT INTO mail_followers(res_model, res_id, partner_id)
             SELECT 'project.project', p.id, u.partner_id
               FROM project_project p
               JOIN project_allowed_portal_users_rel a ON a.project_project_id = p.id
               JOIN res_users u ON u.id = a.res_users_id
              WHERE p.privacy_visibility = 'portal'
                AND u.share = true
        ON CONFLICT DO NOTHING
    """
    )

    # add task allowed users to mail followers if absent
    # reverts migration 13.2.1.1
    cr.execute(
        """
        INSERT INTO mail_followers(res_model, res_id, partner_id)
             SELECT 'project.task', t.id, u.partner_id
               FROM project_task t
               JOIN project_project p ON p.id = t.project_id
               JOIN project_task_res_users_rel a ON a.project_task_id = t.id
               JOIN res_users u ON u.id = a.res_users_id
              WHERE p.privacy_visibility in ('portal', 'followers')
                AND u.share = (p.privacy_visibility = 'portal')
        ON CONFLICT DO NOTHING
    """
    )
    # add task's project allowed users to mail followers if absent
    # reverts migration 13.2.1.1
    cr.execute(
        """
        INSERT INTO mail_followers(res_model, res_id, partner_id)
             SELECT 'project.task', t.id, u.partner_id
               FROM project_task t
               JOIN project_project p ON p.id = t.project_id
               JOIN project_allowed_internal_users_rel a ON a.project_project_id = t.id
               JOIN res_users u ON u.id = a.res_users_id
              WHERE p.privacy_visibility = 'followers'
                AND u.share = false
        ON CONFLICT DO NOTHING
    """
    )
    cr.execute(
        """
        INSERT INTO mail_followers(res_model, res_id, partner_id)
             SELECT 'project.task', t.id, u.partner_id
               FROM project_task t
               JOIN project_project p ON p.id = t.project_id
               JOIN project_allowed_portal_users_rel a ON a.project_project_id = t.id
               JOIN res_users u ON u.id = a.res_users_id
              WHERE p.privacy_visibility = 'portal'
                AND u.share = true
        ON CONFLICT DO NOTHING
    """
    )

    util.update_record_from_xml(cr, "project.project_public_members_rule")
    util.update_record_from_xml(cr, "project.task_visibility_rule")
    util.update_record_from_xml(cr, "project.project_project_rule_portal")
    util.update_record_from_xml(cr, "project.project_task_rule_portal")

    util.remove_field(cr, "project.project", "allowed_user_ids")
    util.remove_field(cr, "project.project", "allowed_internal_user_ids")
    util.remove_field(cr, "project.project", "allowed_portal_user_ids")
    util.remove_field(cr, "project.task", "allowed_user_ids")

    cr.execute("DROP TABLE IF EXISTS project_allowed_internal_users_rel")
    cr.execute("DROP TABLE IF EXISTS project_allowed_portal_users_rel")
    cr.execute("DROP TABLE IF EXISTS project_task_res_users_rel")
