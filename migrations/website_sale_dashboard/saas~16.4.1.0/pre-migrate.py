# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale_dashboard.website_sale_onboarding_payment_provider_step")
    util.remove_view(cr, "website_sale_dashboard.website_sale_dashboard_onboarding_panel")
