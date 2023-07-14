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
    ]
    for ir_rule_xmlid in ir_rule_xmlids_to_update:
        util.if_unchanged(cr, f"project.{ir_rule_xmlid}", util.update_record_from_xml)
