# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "slide.slide.partner", "survey_quizz_passed", "survey_scoring_success")
    # no need to rename survey_closed_finished_inherit_website_slides as parent is removed, it will be removed also
