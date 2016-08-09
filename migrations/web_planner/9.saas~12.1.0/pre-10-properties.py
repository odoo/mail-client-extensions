# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.convert_field_to_property(cr, 'web.planner', 'progress', 'integer', company_field='NULL')
    util.convert_field_to_property(cr, 'web.planner', 'data', 'text', company_field='NULL')
