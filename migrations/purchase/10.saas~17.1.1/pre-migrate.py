# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    util.rename_field(cr, 'stock.config.settings', *eb('{default_new,use}_po_lead'))

    imp = util.import_script('base/10.saas~17.1.3/default_to_icp.py')
    imp.default_to_icp(cr, 'stock.config.settings', 'new_po_lead', 'purchase.use_po_lead')
