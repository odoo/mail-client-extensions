# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_m2m(cr, "project_allowed_internal_users_rel", "project_project", "res_users")
    util.create_m2m(cr, "project_allowed_portal_users_rel", "project_project", "res_users")

    # add all followers' users to the right m2m depending on project visibility and user share flag
    cr.execute(
        """
        INSERT INTO project_allowed_internal_users_rel(project_project_id, res_users_id)
             SELECT p.id, u.id
               FROM project_project p
               JOIN mail_followers f ON f.res_id = p.id AND f.res_model = 'project.project'
               JOIN res_users u ON u.partner_id = f.partner_id
              WHERE p.privacy_visibility = 'followers'
                AND u.share = false
              UNION
             SELECT p.id, u.id
               FROM project_project p
               JOIN mail_followers f ON f.res_id = p.id AND f.res_model = 'project.project'
               JOIN mail_channel_partner c ON c.channel_id = f.channel_id
               JOIN res_users u ON u.partner_id = c.partner_id
              WHERE p.privacy_visibility = 'followers'
                AND u.share = false
    """
    )
    cr.execute(
        """
        INSERT INTO project_allowed_portal_users_rel(project_project_id, res_users_id)
             SELECT DISTINCT p.id, u.id
               FROM project_project p
               JOIN mail_followers f ON f.res_id = p.id AND f.res_model = 'project.project'
               JOIN res_users u ON u.partner_id = f.partner_id
              WHERE p.privacy_visibility = 'portal'
                AND u.share = true
    """
    )

    util.create_m2m(cr, "project_task_res_users_rel", "project_task", "res_users")

    cr.execute(
        """
        INSERT INTO project_task_res_users_rel(project_task_id, res_users_id)
             SELECT t.id, u.id
               FROM project_task t
               JOIN project_project p ON p.id = t.project_id
               JOIN mail_followers f ON f.res_id = t.id AND f.res_model = 'project.task'
               JOIN res_users u ON u.partner_id = f.partner_id
              WHERE p.privacy_visibility IN ('followers', 'portal')
                AND u.share = (p.privacy_visibility = 'portal')
              UNION
             SELECT t.id, r.res_users_id
               FROM project_allowed_internal_users_rel r
               JOIN project_task t ON t.project_id = r.project_project_id
              UNION
             SELECT t.id, r.res_users_id
               FROM project_allowed_portal_users_rel r
               JOIN project_task t ON t.project_id = r.project_project_id
    """
    )

    rules = """
        project_public_members_rule
        task_visibility_rule
        project_project_rule_portal
        project_task_rule_portal
    """
    for rule in util.splitlines(rules):
        util.update_record_from_xml(cr, f"project.{rule}")

    cr.execute(
        """
            UPDATE project_task t
               SET company_id = p.company_id
              FROM project_project p
             WHERE p.id = t.project_id
               AND t.project_id IS NOT NULL
               AND (t.company_id IS NULL OR t.company_id != p.company_id)
        """
    )
