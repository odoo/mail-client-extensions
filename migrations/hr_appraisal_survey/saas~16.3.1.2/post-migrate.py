from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr_appraisal_survey.survey_survey_rule_appraisal_manager")
    util.update_record_from_xml(cr, "survey.survey_user_input_rule_survey_user_read", from_module="hr_appraisal_survey")
