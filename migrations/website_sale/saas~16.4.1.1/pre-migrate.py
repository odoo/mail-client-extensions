# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.company", "website_sale_onboarding_payment_provider_state")
    util.remove_field(cr, "res.config.settings", "terms_url")
    util.remove_field(cr, "product.tag", "ribbon_id")
    util.remove_field(cr, "product.ribbon", "product_tag_ids")

    util.remove_view(cr, "website_sale.res_config_settings_view_form_web_terms")
