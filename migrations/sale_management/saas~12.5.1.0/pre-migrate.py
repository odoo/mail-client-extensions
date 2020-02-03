# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "sale_order_template", "company_id", "int4")
    util.create_column(cr, "sale_order_template_line", "company_id", "int4")
    util.create_column(cr, "sale_order_template_option", "company_id", "int4")

    util.remove_view(cr, "sale_management.sale_order_view_tree")
    util.remove_view(cr, "sale_management.sale_order_view_form")
    util.remove_view(cr, "sale_management.product_template_sale_form_view")

    util.remove_record(cr, "sale_management.menu_product_settings")
    util.remove_record(cr, "sale_management.menu_catalog_variants_action")
