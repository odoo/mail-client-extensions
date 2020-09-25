# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "sale.access_ir_property_sales")
    util.remove_record(cr, "sale.action_open_sale_onboarding_sample_quotation")
    util.remove_view(cr, "sale.sale_onboarding_sample_quotation_form")
