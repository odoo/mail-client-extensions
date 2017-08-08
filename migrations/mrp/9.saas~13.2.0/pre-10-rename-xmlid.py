# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'mrp.mrp_bom_cost', 'mrp.mrp_bom_cost_report')
