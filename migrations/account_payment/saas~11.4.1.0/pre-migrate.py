# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "account.invoice", "payment_acquirer_id")
    for suffix in "ids id count".split():
        util.remove_field(cr, "account.invoice", "payment_tx_" + suffix)

    util.remove_field(cr, "payment.transaction", "account_invoice_id")

    util.remove_view(cr, "account_payment.account_invoice_view_form_inherit_payment")
    util.remove_view(cr, "account_payment.payment_confirmation_status")
    util.remove_view(cr, "account_payment.payment_transaction_view_form")
