# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_field(cr, 'website.config.settings', 'module_website_contract', 'module_website_subscription')

    imp = util.import_script('base/10.saas~17.1.3/default_to_icp.py')
    for g in 'maps analytics analytics_dashboard'.split():
        imp.default_to_icp(cr, 'website.config.settings', 'has_google_' + g, 'website.has_google' + g)
