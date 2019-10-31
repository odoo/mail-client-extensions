# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "gamification_badge", "survey_id", "int4")

    util.remove_field(cr, "survey.survey", "invite_count")
    util.rename_field(cr, "survey.survey", "certified_count", "success_count")
    util.create_column(cr, "survey_survey", "certification_give_badge", "boolean")
    util.create_column(cr, "survey_survey", "certification_badge_id", "int4")

    util.create_column(cr, "survey_user_input", "quizz_score", "float8")

    if not util.table_exists(cr, "survey_question_survey_user_input_rel"):
        # database <saas~12.3. The m2m does not exists. quizz_score is 0
        cr.execute("UPDATE survey_user_input SET quizz_score = 0")
    else:
        cr.execute(
            """
            WITH _total_scores AS (
                SELECT r.survey_user_input_id id, SUM(GREATEST(COALESCE(l.answer_score, 0), 0)) score
                  FROM survey_question_survey_user_input_rel r
                  JOIN survey_label l ON l.question_id = r.survey_question_id
              GROUP BY 1
            ),
            _user_scores AS (
                SELECT user_input_id id, SUM(COALESCE(answer_score, 0)) score
                  FROM survey_user_input_line
              GROUP BY 1
            )
            UPDATE survey_user_input i
               SET quizz_score = ROUND(GREATEST((u.score/t.score)*100, 0)::numeric, 2)
              FROM _total_scores t, _user_scores u
             WHERE u.id = i.id
               AND t.id = i.id
               AND t.score > 0
        """
        )

    util.create_column(cr, "survey_user_input_line", "question_sequence", "int4")
    cr.execute(
        """
        UPDATE survey_user_input_line l
           SET question_sequence = q.sequence
          FROM survey_question q
         WHERE q.id = l.question_id
    """
    )

    eb = util.expand_braces
    util.rename_xmlid(cr, "survey.menu_surveys_configuration", "survey.survey_menu_questions")
    util.rename_xmlid(cr, *eb("survey.survey_user_input{,_view}_search"))
    util.rename_xmlid(cr, *eb("survey.survey_user_input{,_view}_form"))
    util.rename_xmlid(cr, *eb("survey.survey_user_input{,_view}_tree"))
    util.rename_xmlid(cr, *eb("survey.survey_user_input{,_view}_kanban"))
    util.remove_record(cr, "survey.action_survey_user_input_notest")
