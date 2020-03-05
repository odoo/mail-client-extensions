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
