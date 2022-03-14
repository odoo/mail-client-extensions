# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "project_task", "ancestor_id", "int4")

    cr.execute(
        """
        WITH RECURSIVE task_tree AS (
            SELECT id, id as ancestor_id
              FROM project_task
             WHERE parent_id IS NULL
             UNION
            SELECT t.id, tree.ancestor_id
              FROM project_task t
              JOIN task_tree tree ON tree.id = t.parent_id
        )
        UPDATE project_task t
           SET ancestor_id = tree.ancestor_id
          FROM task_tree tree
         WHERE tree.id = t.id
           AND tree.id != tree.ancestor_id
    """
    )

    util.remove_field(cr, "project.task.burndown.chart.report", "nb_tasks")
