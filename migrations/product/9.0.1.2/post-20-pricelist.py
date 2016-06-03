# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # Pricelists are now visible via other groups on either on pricelist themself or the products.
    # Keep current behavior and display the items on pricelists.
    # Also set the "sale" config setting flag.

    env = util.env(cr)
    if env.user.has_group('product.group_sale_pricelist'):
        env['res.groups'].browse(util.ref(cr, 'base.group_user')).write({
            'implied_ids': [(4, util.ref(cr, 'product.group_pricelist_item'))],
        })
        env['ir.values'].set_default('sale.config.settings', 'sale_pricelist_setting', 'formula')
