# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "project_task", "comment", "text")
    cr.execute("DROP VIEW IF EXISTS report_industry_fsm_report_worksheet_custom CASCADE")
    util.rename_model(
        cr,
        "report.industry_fsm_report.worksheet_custom",
        "report.industry_fsm.worksheet_custom",
        rename_table=False,
    )
    util.rename_xmlid(cr, "industry_fsm_report.worksheet_custom", "industry_fsm.worksheet_custom")

    if util.module_installed(cr, "industry_fsm_report"):
        util.rename_xmlid(
            cr, "industry_fsm_report.mail_template_data_send_report", "industry_fsm.mail_template_data_task_report"
        )
        task_fields = util.splitlines(
            """
            allow_worksheets
            worksheet_signature
            worksheet_signed_by
            fsm_is_sent
            display_sign_report_primary
            display_sign_report_secondary
            display_send_report_primary
            display_send_report_secondary
            """
        )
        util.move_field_to_module(cr, "project.project", "allow_worksheets", "industry_fsm_report", "industry_fsm")
        for task_field in task_fields:
            util.move_field_to_module(cr, "project.task", task_field, "industry_fsm_report", "industry_fsm")
    else:
        util.create_column(cr, "project_project", "allow_worksheets", "boolean")
        util.create_column(cr, "project_task", "allow_worksheets", "boolean")
        util.create_column(cr, "project_task", "worksheet_signature", "bytea")
        util.create_column(cr, "project_task", "worksheet_signed_by", "varchar")
        util.create_column(cr, "project_task", "fsm_is_sent", "boolean")
