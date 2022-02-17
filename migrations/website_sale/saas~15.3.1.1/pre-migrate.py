# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "website", "add_to_cart_action", "varchar")
    util.create_column(cr, "website", "account_on_checkout", "varchar", default="optional")
    cr.execute(
        """
        UPDATE website
        SET add_to_cart_action = CASE WHEN cart_add_on_page=true THEN 'stay'
                                      ELSE 'go_to_cart' END"""
    )
    util.remove_field(cr, "website", "cart_add_on_page")
    util.remove_field(cr, "res.config.settings", "cart_add_on_page")

    util.remove_view(cr, "website_sale.website_sale_onboarding_payment_acquirer_step")
    util.remove_model(cr, "website.sale.payment.acquirer.onboarding.wizard")
