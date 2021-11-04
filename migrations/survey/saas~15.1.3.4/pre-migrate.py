# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    for view_type in ["form", "tree", "kanban"]:
        util.rename_xmlid(cr, f"survey.survey_{view_type}", f"survey.survey_survey_view_{view_type}")
    util.create_column(cr, "survey_question", "question_placeholder", "varchar")
