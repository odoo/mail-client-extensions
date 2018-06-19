# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.new_module(cr, 'iap', deps={'web'}, auto_install=True)

    if not util.has_enterprise():
        # moved from enterprise \o/
        util.new_module(cr, 'sms', deps={'iap', 'mail'}, auto_install=True)
        util.new_module(cr, 'calendar_sms', deps={'calendar', 'sms'}, auto_install=True)
    else:
        util.new_module_dep(cr, 'account_accountant', 'account_reports')
        util.new_module_dep(cr, 'sms', 'iap')
        util.remove_module(cr, 'sms_fortytwo')

        util.new_module(cr, 'website_sale_taxcloud_delivery',
                        deps=('website_sale_delivery', 'website_sale_account_taxcloud'),
                        auto_install=True)
