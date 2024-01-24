# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
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
