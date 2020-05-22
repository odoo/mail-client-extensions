# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # session support
    util.rename_field(cr, "survey.survey", "session_show_ranking", "session_show_leaderboard")
    util.create_column(cr, "survey_survey", "session_start_time", "timestamp without time zone")
    util.create_column(cr, "survey_survey", "session_code", "varchar")

    # conditional questions support
    util.create_column(cr, "survey_question", "is_conditional", "boolean")
    util.create_column(cr, "survey_question", "triggering_question_id", "int4")
    util.create_column(cr, "survey_question", "triggering_answer_id", "int4")

    # scoring improvement
    util.create_column(cr, "survey_question", "answer_numerical_box", "float8")
    util.create_column(cr, "survey_question", "answer_date", "date")
    util.create_column(cr, "survey_question", "answer_datetime", "timestamp without time zone")
    util.create_column(cr, "survey_question", "answer_score", "float8")
    util.create_column(cr, "survey_question", "is_scored_question", "bool", default=False)
    # when bootstrapping no question is scored as it is activated by user on new questions
    cr.execute(
        """
        UPDATE survey_question question
           SET is_scored_question = true
          FROM survey_survey survey
         WHERE question.survey_id = survey.id
           AND survey.scoring_type != 'no_scoring'
           AND question.question_type IN ('simple_choice', 'multiple_choice')
        """
    )

    util.create_column(cr, "survey_user_input_line", "answer_is_correct", "bool", default=False)
    # previously only answer_type='suggestion' could be correct/incorrect
    # => make all previously existing non-suggestion answer_types FALSE
    cr.execute(
        """
        UPDATE survey_user_input_line input_line
           SET answer_is_correct = true
          FROM survey_question_answer answer
         WHERE input_line.suggested_answer_id = answer.id
           AND input_line.answer_type = 'suggestion'
           AND answer.is_correct
        """
    )

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("survey.question_result_number{,_or_date}"))
    util.rename_xmlid(cr, *eb("survey.user_input_session_{ranking,leaderboard}"))
    util.rename_xmlid(cr, *eb("survey.survey_{access,session}_code"))
