# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.delete_model(cr, 'report.workcenter.load')
    util.delete_model(cr, 'report.mrp.inout')
    util.delete_model(cr, 'stock.move.comsume')
    util.remove_view(cr, 'mrp.mrp_company')
