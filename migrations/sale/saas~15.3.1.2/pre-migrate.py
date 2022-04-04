# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale.sale_onboarding_order_confirmation_form")
    util.rename_field(cr, "res.config.settings", "module_sale_coupon", "module_sale_loyalty")
