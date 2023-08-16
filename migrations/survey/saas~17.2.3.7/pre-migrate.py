# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "survey_survey", "session_speed_rating_time_limit", "int4")
    util.create_column(cr, "survey_question", "is_time_customized", "boolean", default=False)

    query = """
        UPDATE survey_question
           SET is_time_limited = FALSE
         WHERE is_time_limited IS TRUE
           AND COALESCE(time_limit, 0) = 0
    """
    util.explode_execute(cr, query, table="survey_question")

    query = """
        UPDATE survey_survey
           SET session_speed_rating_time_limit = 30
         WHERE session_speed_rating IS TRUE
    """
    util.explode_execute(cr, query, table="survey_survey")

    # Set as already customized time-limits the questions that have different values from survey
    # configuration to support predictable behavior for the users when updating these values.
    query = """
        UPDATE survey_question q
           SET is_time_customized = TRUE
          FROM survey_survey s
         WHERE q.survey_id = s.id
           AND (COALESCE(s.session_speed_rating, FALSE) <> COALESCE(q.is_time_limited, FALSE)
                OR (q.is_time_limited AND q.time_limit != 30))
    """
    util.explode_execute(cr, query, table="survey_question", alias="q")

    # update of survey management rights: remove former rules become useless

    to_remove = [
        "survey_survey_rule_survey_user_read",
        "survey_survey_rule_survey_user_cwu",
        "survey_question_rule_survey_user_read",
        "survey_question_rule_survey_user_cw",
        "survey_question_answer_rule_survey_user_read",
        "survey_question_answer_rule_survey_user_cw",
        "survey_user_input_rule_survey_user_read",
        "survey_user_input_rule_survey_user_cw",
        "survey_user_input_line_rule_survey_user_read",
        "survey_user_input_line_rule_survey_user_cw",
    ]

    for record_id in to_remove:
        util.remove_record(cr, f"survey.{record_id}")
