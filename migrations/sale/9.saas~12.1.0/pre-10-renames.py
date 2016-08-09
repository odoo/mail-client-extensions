# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    renames = util.splitlines("""
        # menus
        product.menu_product_pricelist_main
        product.menu_product_pricelist_action2
        product.menu_product
        product.menu_product_template_action
        product.prod_config_main
        product.menu_attribute_action
        product.menu_variants_action
        product.menu_products
        product.menu_product_category_action_form
        product.next_id_16
        product.menu_product_uom_form_action
        product.menu_product_uom_categ_form_action
        product.menu_product

        # access rules
        product.access_product_pricelist_item_sale_manager
        product.access_product_price_history_salemanager
        product.access_product_template_sale_manager
        product.access_product_product_sale_manager
        product.access_product_attribute_sale_manager
        product.access_product_attribute_value_sale_manager
        product.access_product_attribute_price_sale_manager
        product.access_product_attribute_line_sale_manager

        account.access_account_tax_sale_manager
        account.access_account_journal_sale_manager
        account.access_account_invoice_tax_sale_manager
        account.access_account_tax_group_sale_manager
        account.access_account_account_sale_manager
    """)
    for r in renames:
        util.rename_xmlid(cr, r, 'sale.' + r.split('.', 1)[1])
