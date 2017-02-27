# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # field change type
    util.remove_field(cr, 'sale.config.settings', 'group_use_lead')

    # wrongly default values' model (see https://github.com/odoo/odoo/pull/15385)
    cr.execute("""
        UPDATE ir_values
           SET model = 'sale.config.settings'
         WHERE model = 'sales.config.settings'
    """)
