# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "rating_status")
    util.remove_field(cr, "res.config.settings", "rating_status_period")
    cr.execute("DELETE FROM ir_config_parameter WHERE key IN ('project.rating_status','project.rating_status_period')")

    util.remove_view(cr, "project.project_milestone_reach_wizard_view_form")
    util.remove_view(cr, "project.project_task_burndown_chart_report_view_pivot")
    util.remove_view(cr, "project.project_collaborator_view_form")
    util.convert_model_to_abstract(cr, "project.task.burndown.chart.report")
    for field in ["date_group_by", "task_id"]:
        util.remove_field(cr, "project.task.burndown.chart.report", field)
    util.remove_model(cr, "project.delete.wizard")

    util.remove_model(cr, "project.milestone.reach.wizard")
    util.remove_model(cr, "project.milestone.reach.line.wizard")
    util.remove_record(cr, "project.unlink_project_action")

    util.remove_field(cr, "project.project", "analytic_tag_ids")
    util.remove_field(cr, "project.task", "analytic_tag_ids")
    # https://github.com/odoo/odoo/pull/101006
    util.if_unchanged(cr, "project.burndown_chart_project_user_rule", util.update_record_from_xml)
