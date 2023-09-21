# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("UPDATE survey_survey SET survey_type = 'appraisal' WHERE is_appraisal")
    util.remove_field(cr, "survey.survey", "is_appraisal")

    util.update_record_from_xml(cr, "hr_appraisal_survey.survey_survey_rule_appraisal_manager")
    util.update_record_from_xml(cr, "survey.survey_user_input_rule_survey_user_read", from_module="hr_appraisal_survey")
