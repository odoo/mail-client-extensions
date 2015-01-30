# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'ir_model_constraint', 'definition', 'varchar')
    util.delete_model(cr, 'ir.sequence.type')
