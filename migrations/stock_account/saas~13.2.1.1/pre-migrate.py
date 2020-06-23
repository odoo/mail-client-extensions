# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "stock.change.standard.price")

    views = """
        view_template_property_form
        product_product_normal_form_view_inherit
        product_variant_easy_edit_view_inherit
    """
    for view in util.splitlines(views):
        util.remove_view(cr, f"stock_account.{view}")
