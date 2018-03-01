# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_field(cr, 'website.config.settings', 'module_website_contract', 'module_website_subscription')

    imp = util.import_script('base/10.saas~17.1.3/default_to_icp.py')
    for g in 'maps analytics analytics_dashboard'.split():
        imp.default_to_icp(cr, 'website.config.settings', 'has_google_' + g, 'website.has_google' + g)

    if util.column_exists(cr, 'website', 'google_management_client_secret'):    # only appear in saas~14
        cr.execute("SELECT count(1) FROM website WHERE COALESCE(google_management_client_secret, '') != ''")
        has = cr.fetchall()[0] > 0
        util.env(cr)['ir.config_parameter'].set_param('website_has_google_analytics_dashboard', has)

    cr.execute("SELECT count(1) FROM website WHERE COALESCE(google_analytics_key, '') != ''")
    has = cr.fetchall()[0] > 0
    util.env(cr)['ir.config_parameter'].set_param('website_has_google_analytics', has)
