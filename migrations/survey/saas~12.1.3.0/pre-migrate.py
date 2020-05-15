# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "survey.question", "type", "question_type")
    util.rename_field(cr, "survey.user_input", "type", "input_type")

    util.rename_model(cr, "survey.mail.compose.message", "survey.invite")
    util.remove_inherit_from_model(
        cr,
        "survey.invite",
        "mail.compose.message",
        keep=(
            "subject",
            "body",
            "attachment_ids",
            "template_id",
            "email_from",
            "author_id",
            "partner_ids",
            "mail_server_id",
        ),
    )

    util.rename_xmlid(cr, "survey.survey_email_compose_message", "survey.survey_invite_view_form")
