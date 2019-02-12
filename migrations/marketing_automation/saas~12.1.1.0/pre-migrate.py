# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'marketing_participant', 'is_test', 'boolean')
    util.create_column(cr, 'marketing_trace', 'is_test', 'boolean')
    cr.execute("update marketing_participant set is_test=FALSE")
    cr.execute("update marketing_trace set is_test=FALSE")
