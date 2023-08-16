# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Update the actions and record rules adapted to the new survey management rights

    util.update_record_from_xml(cr, "base.default_user", from_module="survey")
    util.update_record_from_xml(cr, "base.module_category_marketing_surveys", from_module="survey")

    to_update = [
        "survey_user_input_rule_survey_manager",
        "survey_user_input_line_rule_survey_manager",
        "action_survey_user_input",
        "survey_user_input_line_action",
    ]

    for record_id in to_update:
        util.update_record_from_xml(cr, f"survey.{record_id}")
