# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # there is still some referencing menu to old models (models still there)
    # remove them + all referencing data
    models = ['document.ftp.browse', 'plugin_thunderbird.installer', 'ir.ui.view_sc',
              'google.docs.config']

    ignore = ['ir.model', 'ir.model.data']
    for dest_model, res_model, _ in util.res_model_res_id(cr):
        if dest_model in ignore:
            continue
        table = util.table_of_model(cr, dest_model)
        query = 'DELETE FROM "{0}" WHERE "{1}"=%s'.format(table, res_model)
        for model in models:
            cr.execute(query, (model,))
        util.delete_model(cr, model)
