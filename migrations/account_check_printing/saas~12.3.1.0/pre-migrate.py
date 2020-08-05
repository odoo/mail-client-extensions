# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "account_check_printing.view_account_payment_invoice_form_inherited")
    util.remove_view(cr, "account_check_printing.view_account_payment_from_invoices_inherited")
