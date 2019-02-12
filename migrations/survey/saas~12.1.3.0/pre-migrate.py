# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, 'survey.question', 'type', 'question_type')
    util.rename_model(cr, 'survey.mail.compose.message', 'survey.invite')

    util.rename_xmlid(cr, 'survey.survey_email_compose_message', 'survey.survey_invite_view_form')
