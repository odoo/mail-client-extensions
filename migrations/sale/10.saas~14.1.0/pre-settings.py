# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'account.config.settings', 'group_analytic_account_for_sales')

    fields = util.splitlines("""
        group_product_variant
        group_uom
        group_discount_per_so_line
        module_sale_margin
        group_sale_layout
        group_warning_sale
        module_website_quote
        group_sale_delivery_address
        auto_done_settings

        # type changed & moved to sale_stock
        group_display_incoterm

        # type changed & moved from sale_stock
        module_delivery
    """)
    for f in fields:
        util.remove_field(cr, 'sale.config.settings', f)

    # remove useless res.groups
    util.remove_record(cr, 'sale.group_mrp_properties')
