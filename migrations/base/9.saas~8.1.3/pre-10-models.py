# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'ir_model_fields', 'store', 'boolean')

    util.force_noupdate(cr, 'base.view_model_form', False)
    util.force_noupdate(cr, 'base.view_model_fields_form', False)
