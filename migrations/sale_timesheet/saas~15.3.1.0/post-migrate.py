# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT project.id
          FROM project_project project
          JOIN project_task task ON task.project_id = project.id
         WHERE project.allow_billable IS TRUE
           AND project.sale_line_id IS NOT NULL
           AND task.sale_line_id IS NOT NULL
        """
    )
    ids = [row[0] for row in cr.fetchall()]
    util.recompute_fields(cr, "project.project", ["allocated_hours"], ids=ids)
