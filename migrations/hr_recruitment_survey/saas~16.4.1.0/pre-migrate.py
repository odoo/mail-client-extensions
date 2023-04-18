# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr_recruitment.group_hr_recruitment_user", from_module="hr_recruitment_survey")
    util.update_record_from_xml(
        cr, "survey.survey_user_input_rule_survey_user_read", from_module="hr_recruitment_survey"
    )
