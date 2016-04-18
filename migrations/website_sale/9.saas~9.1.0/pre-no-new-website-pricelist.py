# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # a default `website_pricelist` is added to default website by data file
    # This shouldn't be added if there are other existing pricelist set for the website
    wlist0 = util.ref(cr, 'website_sale.wlist0')
    if wlist0:
        # xid exists => as data are in noupdate, nothing to do.
        return
    website = util.ref(cr, 'website.default_website')
    cr.execute("""
        INSERT INTO ir_model_data(module, name, model, res_id, noupdate)
            SELECT 'website_sale', 'wlist0', 'website_pricelist', min(id), true
              FROM website_pricelist
             WHERE website_id=%s
    """, [website])
