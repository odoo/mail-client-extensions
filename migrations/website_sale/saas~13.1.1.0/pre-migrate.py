# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale.website_sale_pricelist_form_view2")
    util.remove_view(cr, "website_sale.404")
