# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    util.remove_field(cr, "account.report.manager", "partner_id")
    util.remove_field(cr, "account.report.manager", "email_subject")

    util.remove_field(cr, "account_followup.followup.line", "print_letter")
    util.remove_field(cr, "account_followup.followup.line", "manual_action_responsible_id")
    util.rename_field(cr, "account_followup.followup.line", "manual_action", "create_activity")
    util.rename_field(cr, "account_followup.followup.line", *eb("{manual_action,activity}_note"))
    util.rename_field(cr, "account_followup.followup.line", *eb("{manual_action,activity}_type_id"))

    util.rename_field(cr, "account.move.line", "followup_date", "last_followup_date")

    util.rename_field(cr, "res.partner", *eb("{payment,followup}_next_action_date"))
    util.rename_field(cr, "res.partner", *eb("unpaid_{invoices,invoice_ids}"))
    util.rename_field(cr, "res.partner", *eb("followup_{level,line_id}"))
    util.rename_field(cr, "res.partner", *eb("{payment,followup}_responsible_id"))

    util.remove_view(cr, "account_followup.account_move_line_partner_tree")
    util.remove_view(cr, "account_followup.view_move_line_form")
    util.remove_view(cr, "account_followup.line_template_followup_report")

    util.rename_xmlid(cr, *eb("account_followup.property_account_{payment,followup}_next_action_date"))

    util.remove_model(cr, "report.account_followup.report_followup_print_all")

    # Migration of descriptions of followup lines into mail/sms templates
    # - Temporary columns to maintain the mail template associated to each followup line
    util.create_column(cr, "mail_template", "_tmp_followup_line_id", "integer")
    util.create_column(cr, "sms_template", "_tmp_followup_line_id", "integer")

    # - Artificially create template_id and sms_template_id in order to be able to do the following scripts in pre instead of post
    util.create_column(cr, "account_followup_followup_line", "mail_template_id", "integer")
    util.create_column(cr, "account_followup_followup_line", "sms_template_id", "integer")

    # - Convert %(Placeholder)s
    mapping = {
        "%(partner_name)s": "object.name",
        "%(date)s": "fields.Date.today()",
        "%(user_signature)s": "object._get_followup_responsible().signature",
        "%(company_name)s": "object.commercial_partner_id.name",
        "%(amount_due)s": "format_amount(object.total_overdue, object.currency_id)",
    }
    inline_items = []
    qweb_items = []
    for old, new in mapping.items():
        inline_items += [(old, "{{" + new + "}}")]
        qweb_items += [(old, f'<t t-out="{new}"/>')]

    replace_string_1 = util.pg_replace("sms_description", inline_items)
    replace_string_2 = util.pg_replace("email_subject", qweb_items)
    replace_string_3 = util.pg_replace(util.pg_text2html("description"), qweb_items)
    cr.execute(
        f"""
        UPDATE account_followup_followup_line
        SET sms_description = {replace_string_1},
            email_subject = {replace_string_2},
            description = {replace_string_3}
        WHERE send_sms OR send_email
    """
    )

    # - Migration of followup lines into mail template
    cr.execute(
        """
        WITH template_inserted AS (
            INSERT INTO mail_template(name, model_id, subject, body_html,
                                      create_uid, create_date, write_uid, write_date,
                                      _tmp_followup_line_id)
            SELECT jsonb_build_object('en_US', followup_line.name),
                   model.id,
                   jsonb_build_object('en_US', followup_line.email_subject),
                   jsonb_build_object('en_US', followup_line.description),
                   followup_line.create_uid,
                   followup_line.create_date,
                   followup_line.write_uid,
                   followup_line.write_date,
                   followup_line.id
            FROM account_followup_followup_line followup_line
            JOIN ir_model model ON model.model = 'res.partner'
            WHERE followup_line.send_email
            RETURNING id, _tmp_followup_line_id
        )
        UPDATE account_followup_followup_line
        SET mail_template_id = template.id
        FROM template_inserted template
        WHERE template._tmp_followup_line_id = account_followup_followup_line.id
    """
    )

    # - Migration of followup lines into sms template
    cr.execute(
        """
        WITH template_inserted AS (
            INSERT INTO sms_template(name, model_id, body,
                                     create_uid, create_date, write_uid, write_date,
                                     _tmp_followup_line_id)
            SELECT jsonb_build_object('en_US', followup_line.name),
                   model.id,
                   jsonb_build_object('en_US', followup_line.sms_description),
                   followup_line.create_uid,
                   followup_line.create_date,
                   followup_line.write_uid,
                   followup_line.write_date,
                   followup_line.id
            FROM account_followup_followup_line followup_line
            JOIN ir_model model ON model.model = 'res.partner'
            WHERE followup_line.send_sms
            RETURNING id, _tmp_followup_line_id
        )
        UPDATE account_followup_followup_line
        SET sms_template_id = template.id
        FROM template_inserted template
        WHERE template._tmp_followup_line_id = account_followup_followup_line.id
    """
    )

    # - Remove temporary column
    util.remove_column(cr, "mail_template", "_tmp_followup_line_id")
    util.remove_column(cr, "sms_template", "_tmp_followup_line_id")

    util.remove_field(cr, "account_followup.followup.line", "sms_description")
    util.remove_field(cr, "account_followup.followup.line", "description")
    util.remove_field(cr, "account_followup.followup.line", "email_subject")
    util.create_column(cr, "res_partner", "followup_reminder_type", "varchar", default="automatic")
