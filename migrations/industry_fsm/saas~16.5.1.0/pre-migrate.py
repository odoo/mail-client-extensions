# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.remove_view(cr, "industry_fsm.project_task_view_pivot_fsm")
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
    cr.execute("DROP VIEW IF EXISTS report_industry_fsm_worksheet_custom CASCADE")
    if util.module_installed(cr, "industry_fsm_report"):
        util.rename_model(
            cr,
            *eb("report.industry_fsm{,_report}.worksheet_custom"),
            rename_table=False,
        )
        util.rename_xmlid(cr, *eb("industry_fsm{,_report}.worksheet_custom"))
        util.remove_view(cr, "industry_fsm_report.worksheet_custom_page")
        util.rename_xmlid(cr, *eb("industry_fsm{,_report}.worksheet_custom_page"))
        util.rename_xmlid(cr, *eb("industry_fsm{,_report}.mail_template_data_task_report"))
        util.rename_xmlid(cr, *eb("industry_fsm{,_report}.task_custom_report"))
        util.move_field_to_module(cr, "project.project", "allow_worksheets", "industry_fsm", "industry_fsm_report")
        for task_field in task_fields:
            util.move_field_to_module(cr, "project.task", task_field, "industry_fsm", "industry_fsm_report")
    else:
        util.remove_view(cr, "industry_fsm.worksheet_custom")
        util.remove_record(cr, "industry_fsm.task_custom_report")
        util.remove_record(cr, "industry_fsm.mail_template_data_task_report")
        util.remove_model(cr, "report.industry_fsm.worksheet_custom")
        util.remove_view(cr, "industry_fsm.worksheet_custom_page")
        util.remove_field(cr, "project.project", "allow_worksheets")
        for task_field in task_fields:
            util.remove_field(cr, "project.task", task_field)

    # copies the content of comment field into description field
    query = """
        UPDATE project_task
           SET description = CASE
                WHEN description IS NULL OR description = '' THEN comment
                ELSE                                         CONCAT(description, '<hr/>', comment)
               END
         WHERE comment IS NOT NULL AND comment <> ''
    """
    util.explode_execute(cr, query, table="project_task")
    util.remove_field(cr, "project.task", "comment")
    util.remove_view(cr, "industry_fsm.fsm_form_view_comment")
