# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_model(cr, 'survey', 'survey.survey')

    # TODO state => stage (ho yes!)
    # TODO lot of other changes
