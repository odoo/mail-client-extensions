# -*- coding: utf-8 -*-
from odoo.upgrade import util

eb = util.expand_braces


def migrate(cr, version):
    util.rename_field(cr, "purchase.order", *eb("tax_totals{_json,}"))
    util.remove_view(cr, "purchase.product_template_form_view")
    util.remove_view(cr, "purchase.view_category_property_form")
    util.remove_field(cr, "product.template", "property_account_creditor_price_difference")
    util.remove_field(cr, "product.category", "property_account_creditor_price_difference_categ")
