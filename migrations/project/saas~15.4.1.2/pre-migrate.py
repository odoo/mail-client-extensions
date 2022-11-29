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

    util.remove_view(cr, "project.project_report_wizard_form")
    util.remove_record(cr, "project.project_update_all_report_action")
    util.remove_record(cr, "project.project_update_menu_action")
    util.remove_record(cr, "project.project_burndown_chart_report_menu_action")
    util.remove_record(cr, "project.project_burndown_chart_report_action")
    util.remove_model(cr, "project.report.wizard")

    util.create_column(cr, "project_task", "is_blocked", "boolean")

    cr.execute(
        """
        WITH RECURSIVE blocked_task AS (
              SELECT D.task_id AS id
                FROM task_dependencies_rel AS D
                JOIN project_task AS T
                  ON T.id = D.depends_on_id
               WHERE T.is_closed = false
               UNION
              SELECT D1.task_id
                FROM task_dependencies_rel AS D1
                JOIN blocked_task AS B
                  ON D1.depends_on_id = B.id
          )
          UPDATE project_task AS T
             SET is_blocked = true
            FROM blocked_task AS B
           WHERE B.id = T.id
        """
    )

    util.create_column(cr, "project_task", "is_analytic_account_id_changed", "boolean", default=False)
    cr.execute(
        """
            UPDATE project_task t
               SET is_analytic_account_id_changed = true
              FROM project_project p
             WHERE p.id = t.project_id
               AND p.analytic_account_id != t.analytic_account_id
        """
    )
