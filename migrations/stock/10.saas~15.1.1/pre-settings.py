# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    fields = util.splitlines("""
        group_product_variant
        group_uom
        group_stock_packaging
        group_stock_production_lot
        group_stock_tracking_lot
        group_stock_tracking_owner
        group_stock_adv_location
        group_warning_stock

        module_product_expiry
        module_stock_dropshipping
        module_stock_picking_wave
        module_stock_calendar

        warehouse_and_location_usage_level
        decimal_precision
    """)
    for f in fields:
        util.remove_field(cr, 'stock.config.settings', f)

    util.force_noupdate(cr, 'stock.view_stock_config_settings', False)
