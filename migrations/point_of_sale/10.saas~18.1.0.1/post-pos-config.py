# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    has_group = util.env(cr).user.has_group
    params = {
        'sale_pricelist': has_group('product.group_sale_pricelist'),
        'pricelist_item': has_group('product.group_pricelist_item'),
        'loyalty': util.module_installed(cr, 'pos_loyalty'),
        'mercury': util.module_installed(cr, 'pos_mercury'),
        'reprint': util.module_installed(cr, 'pos_reprint'),
    }

    cr.execute("""
        UPDATE pos_config c
           SET iface_tipproduct = (tip_product_id IS NOT NULL),
               use_pricelist = (pricelist_id IS NOT NULL OR %(sale_pricelist)s OR %(pricelist_item)s),
               group_sale_pricelist = %(sale_pricelist)s,
               group_pricelist_item = %(pricelist_item)s,
               tax_regime = (default_fiscal_position_id IS NOT NULL),
               tax_regime_selection = EXISTS(SELECT 1
                                               FROM account_fiscal_position_pos_config_rel
                                              WHERE pos_config_id = c.id),
               barcode_scanner = (barcode_nomenclature_id IS NOT NULL OR iface_scan_via_proxy = true),
               start_category = (iface_start_categ_id  IS NOT NULL),
               is_posbox = (    proxy_ip IS NOT NULL
                             OR iface_scan_via_proxy = true
                             OR iface_electronic_scale = true
                             OR iface_cashdrawer = true
                             OR iface_print_via_proxy = true
                             OR iface_customer_facing_display = true),
               is_header_or_footer = (receipt_header IS NOT NULL OR receipt_footer IS NOT NULL),
               module_pos_restaurant = false,
               module_pos_discount = false,
               module_pos_loyalty = %(loyalty)s,
               module_pos_mercury = %(mercury)s,
               module_pos_reprint = %(reprint)s
    """, params)

    cr.execute("""
        INSERT INTO pos_config_product_pricelist_rel(pos_config_id, product_pricelist_id)
             SELECT c.id, p.id
               FROM pos_config c, product_pricelist p
              WHERE c.company_id = COALESCE(p.company_id, c.company_id)
                AND p.active = true
             EXCEPT
             SELECT pos_config_id, product_pricelist_id
               FROM pos_config_product_pricelist_rel
    """)
