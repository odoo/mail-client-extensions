# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'product_template', 'responsible_id', 'int4')
    cr.execute("UPDATE product_template SET responsible_id = COALESCE(create_uid, %s)",
               [SUPERUSER_ID])

    util.remove_field(cr, 'product.template', 'property_stock_procurement')
    util.remove_model(cr, 'procurement.orderpoint.compute')
