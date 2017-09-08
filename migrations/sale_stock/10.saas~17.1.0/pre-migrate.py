# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_field(cr, 'stock.config.settings', 'default_new_security_lead', 'use_security_lead')
    imp = util.import_script('base/10.saas~17.1.3/default_to_icp.py')
    imp.default_to_icp(cr, 'stock.config.settings', 'use_security_lead', 'sale_stock.use_security_lead')
