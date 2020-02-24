# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # session support
    util.rename_field(cr, 'survey.survey', 'session_show_ranking', 'session_show_leaderboard')
    util.create_column(cr, 'survey_survey', 'session_start_time', 'timestamp without time zone')

    # conditional questions support
    util.create_column(cr, "survey_question", "is_conditional", "boolean")
    util.create_column(cr, "survey_question", "triggering_question_id", "int4")
    util.create_column(cr, "survey_question", "triggering_answer_id", "int4")

    # scoring improvement
    util.create_column(cr, "survey_question", "answer_numerical_box", "float8")
    util.create_column(cr, "survey_question", "answer_date", "date")
    util.create_column(cr, "survey_question", "answer_datetime", "timestamp without time zone")
    util.create_column(cr, "survey_question", "answer_score", "float8")
    util.create_column(cr, "survey_question", "is_scored_question", "bool")
    # when bootstrapping no question is scored as it is activated by user on new questions
    cr.execute("""
        UPDATE survey_question question
        SET is_scored_question = CASE
            WHEN survey.scoring_type = 'no_scoring' THEN FALSE
            WHEN question.question_type = 'simple_choice' THEN TRUE
            WHEN question.question_type = 'multiple_choice' THEN TRUE
            ELSE FALSE END
        FROM survey_survey survey
        WHERE question.survey_id = survey.id
    """)

    util.create_column(cr, "survey_user_input_line", "answer_is_correct", "bool")
    # previously only answer_type='suggestion' could be correct/incorrect
    # => make all previously existing non-suggestion answer_types FALSE
    cr.execute("""
        UPDATE survey_user_input_line input_line
        SET answer_is_correct = CASE
            WHEN input_line.answer_type = 'suggestion' THEN answer.is_correct
            ELSE FALSE
            END
        FROM survey_question_answer answer
        WHERE input_line.suggested_answer_id = answer.id
    """)

    util.rename_xmlid(cr, "survey.question_result_number", "survey.question_result_number_or_date")
