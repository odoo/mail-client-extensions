# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("UPDATE survey_question SET type='date' WHERE type='datetime'")
    util.rename_xmlid(cr, 'survey.datetime', 'survey.date')
    # let orm change column type
