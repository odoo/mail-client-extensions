# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    pp = util.import_script("base/saas~11.3.1.3/pre-parent_path.py")
    pp.parent_path(cr, "product.public.category", "parent_id")

    util.remove_view(cr, "website_sale.product_pricelist_view")
    util.remove_view(cr, "website_sale.product_template_form_view")
    util.remove_view(cr, "website_sale.sale_order_view_form_cart_recovery")
    util.remove_view(cr, "website_sale.sale_order_view_form")

    util.remove_menus(cr, [util.ref(cr, "website_sale.menu_catalog_variants_action")])
