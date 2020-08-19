# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # ===========================================================
    # Account Tour refactor (PR:55624)
    # ===========================================================
    util.remove_view(cr, 'payment.account_invoice_payment_acquirer_onboarding')
