# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "predict_bill_product", "boolean")
    if util.ENVIRON.get("predictive_bills_installed"):
        cr.execute("UPDATE res_company SET predict_bill_product = true")
    util.remove_field(cr, "res.config.settings", "module_account_predictive_bills")
