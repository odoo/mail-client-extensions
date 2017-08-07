# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'mrp.repair.line', 'to_invoice')
    util.remove_field(cr, 'mrp.repair.fee', 'to_invoice')
