# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    for view_type in ["form", "tree", "kanban"]:
        util.rename_xmlid(cr, f"survey.survey_{view_type}", f"survey.survey_survey_view_{view_type}")
    util.remove_record(cr, "survey.survey_action_server_clean_test_answers")
    util.remove_record(cr, "survey.survey_menu_user_inputs")

    util.create_column(cr, "survey_question", "question_placeholder", "varchar")

    util.remove_field(cr, "survey.question", "allow_value_image")
