# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Remove recurrence from subtasks
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """ UPDATE project_task pt
                   SET recurrence_id = NULL
                 WHERE parent_id IS NOT NULL
            """,
            table="project_task",
            alias="pt",
        ),
    )
    util.change_field_selection_values(cr, "project.task", "recurrence_update", {"subsequent": "future"})
