# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # create column to avoid computing a column that will always be NULL
    util.create_column(cr, 'res_partner', 'activity_date_deadline', 'date')
