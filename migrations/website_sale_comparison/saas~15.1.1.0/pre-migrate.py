# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    util.remove_view(cr, "website_sale_comparison.add_to_compare_button")
    util.remove_view(cr, "website_sale_comparison.product_add_to_compare")
