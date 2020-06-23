# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # questions
    util.remove_field(cr, "survey.question", "question")
    util.remove_field(cr, "survey.question", "display_mode")
    util.create_column(cr, "survey_question", "save_as_email", "boolean")
    util.create_column(cr, "survey_question", "save_as_nickname", "boolean")
    util.create_column(cr, "survey_question", "allow_value_image", "boolean")
    util.create_column(cr, "survey_question", "is_time_limited", "boolean")
    util.create_column(cr, "survey_question", "time_limit", "integer")
    util.rename_field(cr, "survey.question", "labels_ids", "suggested_answer_ids")
    util.rename_field(cr, "survey.question", "labels_ids_2", "matrix_row_ids")

    cr.execute("UPDATE survey_question SET question_type = 'text_box' WHERE question_type = 'free_text'")
    cr.execute("UPDATE survey_question SET question_type = 'char_box' WHERE question_type = 'textbox'")

    # answers
    util.rename_model(cr, "survey.label", "survey.question.answer")
    util.rename_field(cr, "survey.question.answer", "question_id_2", "matrix_question_id")

    # surveys
    util.remove_field(cr, "survey.survey", "category")
    util.remove_field(cr, "survey.survey", "public_url")
    util.rename_field(cr, "survey.survey", "thank_you_message", "description_done")
    util.rename_field(cr, "survey.survey", "passing_score", "scoring_success_min")
    util.rename_field(cr, "survey.survey", "certificate", "certification")
    util.create_column(cr, "survey_survey", "progression_mode", "varchar")
    util.create_column(cr, "survey_survey", "session_state", "varchar")
    util.create_column(cr, "survey_survey", "session_question_id", "integer")
    util.create_column(cr, "survey_survey", "session_question_start_time", "timestamp")
    util.create_column(cr, "survey_survey", "session_speed_rating", "boolean")

    cr.execute(
        """
        ALTER TABLE survey_survey
        RENAME CONSTRAINT survey_survey_certificate_check TO survey_survey_certification_check
    """
    )
    cr.execute("UPDATE survey_survey SET progression_mode = 'percent'")

    # user inputs
    util.remove_field(cr, "survey.user_input", "input_type")
    util.create_column(cr, "survey_user_input", "nickname", "varchar")
    util.create_column(cr, "survey_user_input", "scoring_total", "float8")
    util.create_column(cr, "survey_user_input", "is_session_answer", "boolean")

    util.rename_field(cr, "survey.user_input", "attempt_number", "attempts_number")
    util.rename_field(cr, "survey.user_input", "is_time_limit_reached", "survey_time_limit_reached")
    util.rename_field(cr, "survey.user_input", "token", "access_token")
    util.rename_field(cr, "survey.user_input", "question_ids", "predefined_question_ids")
    util.rename_field(cr, "survey.user_input", "quizz_score", "scoring_percentage")
    util.rename_field(cr, "survey.user_input", "quizz_passed", "scoring_success")

    cr.execute("UPDATE survey_user_input SET state='in_progress' WHERE state='skip'")
    cr.execute(
        """
        WITH score AS (
            SELECT i.id, COALESCE(SUM(COALESCE(l.answer_score, 0)), 0) as score
              FROM survey_user_input i
         LEFT JOIN survey_user_input_line l ON l.user_input_id = i.id
          GROUP BY i.id
        )
        UPDATE survey_user_input i
           SET scoring_total = s.score
          FROM score s
         WHERE s.id = i.id
    """
    )

    # input lines
    util.rename_model(cr, "survey.user_input_line", "survey.user_input.line", rename_table=False)

    util.rename_field(cr, "survey.user_input.line", "value_text", "value_char_box")
    util.rename_field(cr, "survey.user_input.line", "value_number", "value_numerical_box")
    util.rename_field(cr, "survey.user_input.line", "value_free_text", "value_text_box")
    util.rename_field(cr, "survey.user_input.line", "value_suggested", "suggested_answer_id")
    util.rename_field(cr, "survey.user_input.line", "value_suggested_row", "matrix_row_id")

    cr.execute(
        """
        UPDATE survey_user_input_line
           SET answer_type = CASE answer_type WHEN 'text' THEN 'char_box'
                                              WHEN 'number' THEN 'numerical_box'
                                              WHEN 'free_text' THEN 'text_box'
                              END
         WHERE answer_type IN ('text', 'number', 'free_text')
    """
    )

    # wizard
    util.rename_field(cr, "survey.invite", "survey_url", "survey_start_url")

    # data
    eb = util.expand_braces
    renames = """
        access_survey_{label,question_answer}_all
        access_survey_{label,question_answer}_user
        access_survey_{label,question_answer}_survey_user
        access_survey_{label,question_answer}_survey_manager

        survey_{label,question_answer}_rule_survey_manager
        survey_{label,question_answer}_rule_survey_user_read
        survey_{label,question_answer}_rule_survey_user_cw

        selection__survey_user_input_line__answer_type__{free_text,text_box}
        selection__survey_user_input_line__answer_type__{number,numerical_box}
        selection__survey_user_input_line__answer_type__{text,char_box}

        # views
        survey_{label,question_answer_view}_tree
        survey_{label,question_answer_view}_search
        {action_survey_label_form,survey_question_answer_action}
        survey_user_input_line_{,view_}form
        survey_response_line_{,view_}tree
        survey_{response_line,user_input_line_view}_search
        {action_survey_user_input_line,survey_user_input_line_action}

        # templates
        question_{free_text,text_box}
        question_{textbox,char_box}
        question_{,table_}pagination
    """
    for rename in util.splitlines(renames):
        util.rename_xmlid(cr, *eb(f"survey.{rename}"))

    for suffix in "start main content main_header".split():
        util.remove_view(cr, f"survey.survey_page_{suffix}")
    util.remove_view(cr, "survey.survey_closed_finished")
