# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.delete_model(cr, 'purchase.requisition.partner')
    util.delete_model(cr, 'bid.line.qty')
    util.drop_workflow(cr, 'pruchase.requisition')
