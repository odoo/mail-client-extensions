# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_field(cr, 'procurement.group', 'sale_order_id', 'sale_id')
