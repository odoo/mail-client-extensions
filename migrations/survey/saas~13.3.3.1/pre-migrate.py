# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, 'survey.survey', 'session_show_ranking', 'session_show_leaderboard')
    util.create_column(cr, 'survey_survey', 'session_start_time', 'timestamp without time zone')
