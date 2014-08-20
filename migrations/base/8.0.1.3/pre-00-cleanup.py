# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # there is still some referencing menu to old models (models still there)
    # remove them + all referencing data
    models = ['document.ftp.browse', 'ir.ui.view_sc', 'google.docs.config']
    for model in models:
        util.delete_model(cr, model)
