# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'sale_subscription_line', 'price_subtotal', 'numeric')

    # template is not correct in data, keep actual
    util.force_noupdate(cr, 'sale_subscription.email_subscription_open', True)
