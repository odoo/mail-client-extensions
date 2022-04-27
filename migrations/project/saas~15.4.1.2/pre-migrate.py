# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
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
    if util.module_installed(cr, "project_enterprise"):
        renames = [
            eb("project{_enterprise,}.project_task_kanban_action_view"),
            eb("project{_enterprise,}.project_task_tree_action_view"),
            eb("project{_enterprise,}.project_task_form_action_view"),
            eb("project{_enterprise,}.project_all_task_calendar_action_view"),
            eb("project{_enterprise,}.project_all_task_pivot_action_view"),
            eb("project{_enterprise,}.project_all_task_graph_action_view"),
            eb("project{_enterprise,}.project_all_task_activity_action_view"),
        ]

        for rename in renames:
            util.rename_xmlid(cr, *rename)
