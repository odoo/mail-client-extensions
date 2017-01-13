# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    fields = util.splitlines("""
        # type changed
        group_product_variant
        group_uom
        module_purchase_requisition
        group_warning_purchase
        module_stock_dropshipping
        group_manage_vendor_price

        # removed
        group_costing_method
    """)
    for f in fields:
        util.remove_field(cr, 'purchase.config.settings', f)

    util.remove_view(cr, 'purchase.view_purchase_configuration')
