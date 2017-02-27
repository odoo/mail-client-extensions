# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    fields = util.splitlines("""
        module_delivery_temando
        group_website_multiimage
        module_website_sale_options
        sale_pricelist_setting_split_1
    """)
    for f in fields:
        util.remove_field(cr, 'website.config.settings', f)
