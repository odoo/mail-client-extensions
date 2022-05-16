# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_stock.product_template_view_form_inherit_stock")
    util.remove_view(cr, "sale_stock.product_template_view_form_inherit_sale")
