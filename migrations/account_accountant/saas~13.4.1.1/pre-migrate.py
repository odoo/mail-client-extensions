# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_accountant.account_payment_view_form")
    util.remove_view(cr, "account_accountant.view_account_payment_form")

    util.remove_menus(cr, [util.ref(cr, "account_accountant.menu_product_product_categories")])
