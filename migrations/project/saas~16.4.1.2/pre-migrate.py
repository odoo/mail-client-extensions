# -*- coding: utf-8 -*-

from odoo.upgrade import util


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

    ir_rule_xmlids_to_update = [
        "project_comp_rule",
        "task_comp_rule",
        "report_project_task_user_report_comp_rule",
        "update_comp_rule",
        "milestone_comp_rule",
        "project_manager_all_project_tasks_rule",
    ]
    for ir_rule_xmlid in ir_rule_xmlids_to_update:
        util.if_unchanged(cr, f"project.{ir_rule_xmlid}", util.update_record_from_xml)

    util.remove_field(cr, "project.task", "is_private")
    util.update_field_usage(cr, "project.task", "project_root_id", "project_id")
    util.remove_field(cr, "project.task", "project_root_id")
    # Create the column "display_in_project"
    util.create_column(cr, "project_task", "display_in_project", "boolean", default=True)
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
