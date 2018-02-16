# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    util.rename_field(cr, 'pos.config.settings', *eb('{default,use_pos}_sale_price'))
    util.rename_field(cr, 'pos.config.settings', *eb('{default,pos}_pricelist_setting'))

    imp = util.import_script('base/10.saas~17.1.3/default_to_icp.py')
    imp.default_to_icp(cr, 'pos.config.settings', 'sale_price', 'pos.use_pos_sale_price')
    imp.default_to_icp(cr, 'pos.config.settings', 'pricelist_setting', 'pos.pos_pricelist_setting')
