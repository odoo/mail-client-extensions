# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # ===========================================================
    # Invoice Analysis (PR:47066)
    # ===========================================================
    util.rename_field(cr, 'account.invoice.report', 'currency_id', 'company_currency_id')
    for field in ['name', 'invoice_payment_term_id', 'invoice_partner_bank_id', 'nbr_lines', 'residual', 'amount_total']:
        util.remove_field(cr, 'account.invoice.report', field)
