# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "appraisal_ask_feedback", "lang", "varchar")
