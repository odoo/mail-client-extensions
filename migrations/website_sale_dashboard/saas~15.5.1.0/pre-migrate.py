# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale_dashboard.res_config_settings_view_form")
    util.rename_xmlid(
        cr,
        "website_sale_dashboard.website_sale_onboarding_payment_acquirer_step",
        "website_sale_dashboard.website_sale_onboarding_payment_provider_step",
    )
