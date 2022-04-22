# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale.product_edit_options")
    util.remove_view(cr, "website_sale.search_count_box")
    util.remove_view(cr, "website_sale.user_navbar_inherit_website_sale")
