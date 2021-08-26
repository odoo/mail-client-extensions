# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_stock_renting.product_product_inherit_view_form_stock")
    util.remove_view(cr, "sale_stock_renting.product_template_inherit_view_form_stock")
