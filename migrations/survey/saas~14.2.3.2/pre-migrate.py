# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_constraint(cr, "survey_survey", "survey_survey_give_badge_check")
