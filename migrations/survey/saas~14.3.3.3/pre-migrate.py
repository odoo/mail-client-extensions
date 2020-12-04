# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "survey_survey", "user_id", "int4")
    cr.execute("UPDATE survey_survey SET user_id=create_uid")
    cr.execute("UPDATE survey_survey SET active=false WHERE state='closed'")
    util.remove_field(cr, "survey.survey", "state")
