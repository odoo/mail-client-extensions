# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.force_noupdate(cr, 'delivery.product_packaging_delivery_form', False)
    util.force_noupdate(cr, 'delivery.product_packaging_delivery_tree', False)
    util.force_noupdate(cr, 'delivery.choose_delivery_package_view_form', False)
