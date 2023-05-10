# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr_appraisal_survey.mail_template_appraisal_ask_feedback")
    util.remove_field(cr, "appraisal.ask.feedback", "user_body")
