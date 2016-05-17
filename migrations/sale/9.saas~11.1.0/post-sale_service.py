# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if util.ENVIRON.get('sale_layout_installed'):
        # remove some old views
        for v, i in [('order', 1), ('invoice', 1), ('invoice_line', 2)]:
            util.remove_view(cr, 'sale.view_{0}_form_inherit_{1}'.format(v, i))

        env = util.env(cr)
        cfg = env['sale.config.settings'].create({'group_sale_layout': 1})
        cfg.execute()
