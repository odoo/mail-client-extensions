# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    util.rename_field(cr, "product.template", *eb("{report,worksheet}_template_id"))
    util.rename_field(cr, "project.project", *eb("allow_{reports,worksheets}"))
    util.rename_field(cr, "project.project", *eb("{report,worksheet}_template_id"))
    util.rename_field(cr, "project.task", *eb("allow_{reports,worksheets}"))
    util.rename_field(cr, "project.task", *eb("{report,worksheet}_template_id"))
    util.rename_field(cr, "project.task", *eb("{report,worksheet}_count"))
    util.create_column(cr, "project_task", "fsm_is_sent", "boolean")  # cannot fill it

    util.rename_model(cr, *eb("project.{report,worksheet}.template"))
    util.rename_field(cr, "project.worksheet.template", *eb("{report,worksheet}_count"))
    util.create_column(cr, "project_worksheet_template", "report_view_id", "int4")

    util.rename_xmlid(cr, *eb("industry_fsm_report.fsm_{report,worksheet}_template"))
    util.rename_xmlid(cr, *eb("industry_fsm_report.access_project_{report,worksheet}_template"))
    util.rename_xmlid(cr, *eb("industry_fsm_report.access_project_{report,worksheet}_template_manager"))
    util.rename_xmlid(cr, *eb("industry_fsm_report.project_{report,worksheet}_template_view_form"))
    util.rename_xmlid(cr, *eb("industry_fsm_report.project_{report,worksheet}_template_view_list"))
    util.rename_xmlid(cr, *eb("industry_fsm_report.project_{report,worksheet}_template_menu"))
    util.rename_xmlid(cr, *eb("industry_fsm_report.action_fsm_{reports,worksheets}"))
    util.rename_xmlid(cr, *eb("industry_fsm_report.project_task_view_form_{fsm_,}inherit"))
