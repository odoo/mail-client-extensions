# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Replace survey.triggering_answer_id to m2m relationship
    util.create_m2m(cr, "survey_question_survey_question_answer_rel", "survey_question", "survey_question_answer")
    cr.execute(
        """
        INSERT INTO survey_question_survey_question_answer_rel(survey_question_id, survey_question_answer_id)
             SELECT id, triggering_answer_id
               FROM survey_question
              WHERE triggering_answer_id IS NOT NULL
        """
    )
    util.remove_field(cr, "survey.question", "is_conditional")
    util.remove_field(cr, "survey.question", "triggering_answer_id")
    util.remove_field(cr, "survey.question", "triggering_question_id")
