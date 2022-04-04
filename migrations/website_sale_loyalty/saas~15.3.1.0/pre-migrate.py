# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "loyalty.card", "website_id")

    util.remove_view(cr, "website_sale_loyalty.res_config_settings_view_form")
    util.remove_view(cr, "website_sale_loyalty.add_gift_card")
    util.remove_view(cr, "website_sale_loyalty.gift_card_view_search")
    util.remove_view(cr, "website_sale_loyalty.gift_card_view_form")
    util.remove_view(cr, "website_sale_loyalty.sale_coupon_program_view_tree_website")
    util.remove_view(cr, "website_sale_loyalty.sale_coupon_program_view_form_common_website")
    util.remove_view(cr, "website_sale_loyalty.coupon_view_tree")
