# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record(cr, "website_sale.payment_transaction_action_payments_to_capture")
    util.remove_view(cr, "website_sale.payment_transaction_view_form_inherit_website_sale")
    util.remove_view(cr, "website_sale.report_shop_saleorder_document")
