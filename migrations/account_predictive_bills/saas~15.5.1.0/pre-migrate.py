# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_predictive_bills.predictive_data_vendor_bill_form")
    util.remove_field(cr, "account.move.line", "predict_from_name")
