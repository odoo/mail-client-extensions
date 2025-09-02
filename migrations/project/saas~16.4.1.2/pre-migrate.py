from odoo.upgrade import util
from odoo.upgrade.util.inconsistencies import break_recursive_loops


def migrate(cr, version):
    def is_closed_adapter(leaf, _o, _n):
        # what was closed is now in one of the closed states
        _, op, right = leaf
        return [("state", "in" if (op == "=") == right else "not in", ["1_done", "1_canceled"])]

    util.update_field_usage(cr, "project.task", "is_closed", "state", domain_adapter=is_closed_adapter)

    util.remove_field(cr, "project.task", "is_closed")
    util.remove_field(cr, "project.task.burndown.chart.report", "is_closed")
    util.remove_field(cr, "report.project.task.user", "is_closed")
    util.remove_field(cr, "project.task", "allow_recurring_tasks")
    util.remove_field(cr, "project.project", "allow_recurring_tasks")

    util.remove_field(cr, "project.task", "is_private")
    util.update_field_usage(cr, "project.task", "project_root_id", "project_id")
    util.remove_field(cr, "project.task", "project_root_id")
    # Create the column "display_in_project"
    util.create_column(cr, "project_task", "display_in_project", "boolean", default=True)
    if util.column_exists(cr, "project_task", "display_project_id"):
        util.explode_execute(
            cr,
            """
            UPDATE project_task pt
               SET display_in_project = false
             WHERE display_project_id IS NULL
            """,
            table="project_task",
            alias="pt",
        )
    # Before running a recursive query, break any loops in the recursive data
    break_recursive_loops(cr, "project.task", "parent_id")
    # Set "project_id" of all non-private tasks to their project root
    # and "display_in_project" to false
    util.explode_execute(
        cr,
        """
        WITH RECURSIVE project_hierarchy AS (
                    SELECT pt.id,
                           pt.parent_id,
                           pt.project_id AS project_root_id
                      FROM project_task pt
                     WHERE pt.project_id IS NULL
                       AND pt.parent_id IS NOT NULL
                       AND {parallel_filter}
                 UNION ALL
                    SELECT ph.id,
                           pt.parent_id,
                           COALESCE(ph.project_root_id, pt.project_id) AS project_root_id
                      FROM project_hierarchy ph
                      JOIN project_task pt ON ph.parent_id = pt.id
                       )
                UPDATE project_task pt
                   SET project_id = ph.project_root_id,
                       display_in_project = false
                  FROM project_hierarchy ph
                 WHERE ph.project_root_id IS NOT NULL
                   AND ph.id = pt.id
        """,
        table="project_task",
        alias="pt",
    )

    if util.module_installed(cr, "planning"):
        util.move_field_to_module(cr, "res.config.settings", "module_project_forecast", "project", "planning")
    else:
        util.remove_field(cr, "res.config.settings", "module_project_forecast")

        cr.execute(
            """
            UPDATE project_project
               SET task_properties_definition = (
                    SELECT jsonb_agg(
                      CASE WHEN def ? 'view_in_kanban'
                           THEN def - 'view_in_kanban' || jsonb_build_object('view_in_cards', def->'view_in_kanban')
                           ELSE def
                       END
               )      FROM jsonb_array_elements(task_properties_definition) AS elem(def)
            )
             WHERE jsonb_path_exists(task_properties_definition, '$[*]."view_in_kanban"')
            """
        )
