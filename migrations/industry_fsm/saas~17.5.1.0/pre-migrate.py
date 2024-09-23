from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    cr.execute(
        """
        UPDATE ir_act_window
           SET path=NULL
         WHERE id=%s
           AND path='field-service'
        """,
        [util.ref(cr, "industry_fsm.project_task_action_fsm")],
    )
    if util.module_installed(cr, "industry_fsm_report"):
        util.rename_xmlid(cr, *eb("industry_fsm{_report,}.worksheet_custom"))
        util.rename_xmlid(cr, *eb("industry_fsm{_report,}.mail_template_data_task_report"))
        util.rename_xmlid(cr, *eb("industry_fsm{_report,}.task_custom_report"))
        util.rename_model(cr, *eb("report.industry_fsm{_report,}.worksheet_custom"))

        util.move_field_to_module(cr, "project.task", "worksheet_signature", "industry_fsm_report", "industry_fsm")
        util.move_field_to_module(cr, "project.task", "worksheet_signed_by", "industry_fsm_report", "industry_fsm")
        util.move_field_to_module(cr, "project.task", "fsm_is_sent", "industry_fsm_report", "industry_fsm")
        util.move_field_to_module(
            cr, "project.task", "display_sign_report_primary", "industry_fsm_report", "industry_fsm"
        )
        util.move_field_to_module(
            cr, "project.task", "display_sign_report_secondary", "industry_fsm_report", "industry_fsm"
        )
        util.move_field_to_module(
            cr, "project.task", "display_send_report_primary", "industry_fsm_report", "industry_fsm"
        )
        util.move_field_to_module(
            cr, "project.task", "display_send_report_secondary", "industry_fsm_report", "industry_fsm"
        )
