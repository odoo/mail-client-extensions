# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    update_records = [
        "hr_appraisal_survey.survey_user_input_rule_appraisal_user",
        "hr_appraisal_survey.survey_user_input_line_rule_appraisal_user",
        "hr_appraisal_survey.survey_user_input_rule_appraisal_employee_manager",
        "hr_appraisal_survey.survey_user_input_line_rule_appraisal_employee_manager",
        "hr_appraisal_survey.survey_question_rule_appraisal_employee_manager",
    ]

    for record in update_records:
        util.update_record_from_xml(cr, record)
