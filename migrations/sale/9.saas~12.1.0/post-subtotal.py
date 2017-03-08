# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.env(cr)['sale.config.settings'].create({
        'sale_show_tax': 'subtotal',
        'group_show_price_total': False,
        'group_show_price_subtotal': True,
    }).execute()
