# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # move model_is_thread from mass mailing to mail; otherwise as it is not
    # stored do nothing
    if util.module_installed(cr, "mass_mailing"):
        util.move_field_to_module(cr, "mail.compose.message", "model_is_thread", "mass_mailing", "mail")

    # move from res_id (+ active_ids context) to either res_ids, either res_domain (with user for search)
    util.create_column(cr, "mail_compose_message", "auto_delete_keep_log", "boolean")
    util.create_column(cr, "mail_compose_message", "force_send", "boolean", default=True)
    util.create_column(cr, "mail_compose_message", "res_domain_user_id", "int4")
    util.create_column(cr, "mail_compose_message", "res_ids", "text")
    util.create_column(cr, "mail_compose_message", "use_exclusion_list", "boolean", default=True)
    cr.execute(
        """
        UPDATE mail_compose_message
           SET auto_delete_keep_log = CASE WHEN auto_delete_message IS TRUE THEN FALSE
                                      ELSE TRUE
                                      END
    """
    )
    cr.execute(
        """
        UPDATE mail_compose_message
           SET res_ids = CASE WHEN coalesce(res_id, 0) <> 0 THEN CONCAT('[', res_id, ']')
                              ELSE NULL
                              END
    """
    )
    util.remove_field(cr, "mail.compose.message", "auto_delete_message")
    util.remove_field(cr, "mail.compose.message", "is_log")
    util.remove_field(cr, "mail.compose.message", "notify")
    util.remove_field(cr, "mail.compose.message", "res_id")
    util.remove_field(cr, "mail.compose.message", "use_active_domain")
    util.rename_field(cr, "mail.compose.message", "active_domain", "res_domain")
    util.change_field_selection_values(
        cr,
        "mail.compose.message",
        "composition_mode",
        {"mass_post": "comment"},
    )

    # move from report_template (m2o) to report_template_ids (m2m)
    util.create_m2m(
        cr,
        "mail_template_ir_actions_report_rel",
        "mail_template",
        "ir_act_report_xml",
        col1="mail_template_id",
        col2="ir_actions_report_id",
    )
    cr.execute(
        """
        INSERT INTO mail_template_ir_actions_report_rel(mail_template_id, ir_actions_report_id)
             SELECT id, report_template
               FROM mail_template
              WHERE report_template IS NOT NULL;
    """
    )
    util.remove_field(cr, "mail.template", "report_template")
    util.remove_field(cr, "mail.template", "report_name")
    util.create_column(cr, "mail_template", "email_layout_xmlid", "varchar")

    util.remove_field(cr, "mail.mail", "to_delete")

    # Remove message_main_attachment_id field from mail.thread models except the ones inheriting from mail.thread.main.attachment
    util.remove_field(
        cr,
        "mail.thread",
        "message_main_attachment_id",
        skip_inherit=(
            "account.move",
            "account.payment",
            "approval.request",
            "extract.mixin",
            "hr.applicant",
            "hr.employee",
            "hr.expense",
            "hr.expense.sheet",
            "hr.leave",
            "hr.payslip",
            "sdd.mandate",
        ),
    )
    # Remove message_main_attachment_id field from mail.thread *manual* models
    cr.execute("SELECT model FROM ir_model WHERE is_mail_thread AND state = 'manual'")
    manual_models = [r[0] for r in cr.fetchall()]
    util._logger.info("Remove message_main_attachment_id from manual models: %s", manual_models)
    for model in manual_models:
        util.remove_field(cr, model, "message_main_attachment_id")
