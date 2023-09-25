# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "report.product.report_producttemplatelabel")
    util.remove_view(cr, "product.report_producttemplatelabel")
    # Product catalog views moved from `sale` to `product`.
    util.rename_xmlid(cr, "sale.sale_product_catalog_kanban_view", "product.product_view_kanban_catalog")
    util.rename_xmlid(cr, "sale.sale_product_catalog_search_view", "product.product_view_search_catalog")
