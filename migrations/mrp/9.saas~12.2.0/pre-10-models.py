# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_model(cr, 'mrp.production.workcenter.line', 'mrp.workorder')
    util.drop_workflow(cr, 'mrp.production')
