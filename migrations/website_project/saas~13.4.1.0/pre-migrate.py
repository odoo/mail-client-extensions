# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    util.create_column(cr, "project_project", "is_published", "boolean")

    cr.execute(
        """
        UPDATE project_project
        SET is_published =
        CASE
            WHEN portal_show_rating = TRUE OR portal_show_rating is NULL THEN TRUE
            WHEN portal_show_rating = FALSE THEN FALSE
            ELSE FALSE END"""
    )
