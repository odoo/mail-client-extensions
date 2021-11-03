# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, *util.expand_braces("survey.question_result_number_or_date{,_or_datetime}"))
