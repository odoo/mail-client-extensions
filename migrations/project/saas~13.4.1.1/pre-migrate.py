# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "project_project", "rating_active", "boolean")
    cr.execute(
        """
        UPDATE project_project
           SET rating_active = CASE WHEN rating_status = 'no' THEN FALSE ELSE TRUE END,
               rating_status = CASE WHEN rating_status = 'no' THEN 'stage' ELSE rating_status END"""
    )

    cr.execute(
        """
        UPDATE project_project
        SET rating_status_period='monthly'
        WHERE rating_status_period IS NULL"""
    )

    util.force_noupdate(cr, "project.rating_project_request_email_template", False)

    util.remove_field(cr, 'project.task', 'date_deadline_formatted')

    util.create_column(cr, "project_project", "allow_subtasks", "boolean")
    group_subtask = util.env(cr).ref("project.group_subtask_project")
    cr.execute(
        """
        UPDATE project_project
           SET allow_subtasks = g.uid IS NOT NULL
          FROM res_groups_users_rel g
         WHERE g.gid = %s
        """,
        (group_subtask.id,),
    )

    util.update_record_from_xml(cr, "project.digest_tip_project_0")
