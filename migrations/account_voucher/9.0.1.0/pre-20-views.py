# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    view_list = util.splitlines("""
        view_vendor_receipt_form
        view_vendor_payment_form
        view_voucher_filter_vendor_pay
        view_voucher_filter_customer_pay
        view_voucher_form
        view_invoice_customer
        view_invoice_supplier
    """)
    for view in view_list:
        util.remove_view(cr, "account_voucher." + view)
