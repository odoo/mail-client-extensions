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
