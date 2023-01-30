# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.adapt_domains(cr, "project.project", "commercial_partner_id", "partner_id.commercial_partner_id")
    util.remove_field(cr, "project.project", "commercial_partner_id")

    util.adapt_domains(cr, "project.task", "commercial_partner_id", "partner_id.commercial_partner_id")
    util.remove_field(cr, "project.task", "commercial_partner_id")

    util.adapt_domains(cr, "project.task", "project_color", "project_id.color")
    util.remove_field(cr, "project.task", "project_color")

    util.adapt_domains(cr, "project.task", "display_project_id", "project_id")

    util.remove_field(cr, "project.task", "display_project_id")
    util.remove_field(cr, "project.project", "task_count_with_subtasks")
    util.remove_field(cr, "project.task.burndown.chart.report", "display_project_id")
    util.remove_field(cr, "project.task.burndown.chart.report", "has_late_and_unreached_milestone")

    if not util.module_installed(cr, "industry_fsm"):
        util.remove_field(cr, "project.task", "partner_phone")
        util.remove_field(cr, "project.task", "partner_city")
    else:
        util.move_field_to_module(cr, "project.task", "partner_phone", "project", "industry_fsm")
        util.move_field_to_module(cr, "project.task", "partner_city", "project", "industry_fsm")
