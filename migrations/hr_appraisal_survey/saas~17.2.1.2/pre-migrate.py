# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    rename_records = [
        "hr_appraisal_survey.survey_user_input_rule_appraisal_simple_manager",
        "hr_appraisal_survey.survey_user_input_line_rule_appraisal_simple_manager",
        "hr_appraisal_survey.survey_question_rule_appraisal_simple_manager",
    ]

    for record in rename_records:
        util.rename_xmlid(cr, record, record.replace("simple", "employee"))

    # Create and fill new relational table between surveys linked to appraisals
    # and appraisals managers
    util.create_m2m(cr, "survey_survey_res_users_appraisal_rel", "survey_survey", "res_users")

    query = """
    INSERT INTO survey_survey_res_users_appraisal_rel (survey_survey_id, res_users_id)
         SELECT sui.survey_id, hre.user_id
           FROM survey_user_input sui
           JOIN appraisal_manager_rel am
             ON sui.appraisal_id = am.hr_appraisal_id
           JOIN hr_employee hre
             ON am.hr_employee_id = hre.id
       GROUP BY sui.survey_id, hre.user_id
    """

    cr.execute(query)
