# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Removing here as also used in account_payment and website_sale_dashboard.
    util.remove_field(cr, "res.company", "payment_provider_onboarding_state")
