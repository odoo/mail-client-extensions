# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "helpdesk_ticket", "email_cc", "varchar")

    mapping = {
        "use_credit_notes": "helpdesk_account",
        "use_coupons": "helpdesk_sale_coupon",
        "use_product_returns": "helpdesk_stock",
        "use_product_repairs": "helpdesk_repair",
    }
    for field, module in mapping.items():
        util.create_column(cr, "helpdesk_team", field, "boolean")
        if util.module_installed(cr, module):
            cr.execute("UPDATE helpdesk_team SET {} = true".format(field))
