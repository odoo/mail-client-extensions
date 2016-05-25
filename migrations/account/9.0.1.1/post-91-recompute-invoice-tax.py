# -*- coding: utf-8 -*-
from operator import itemgetter
from openerp.addons.base.maintenance.migrations import util

def update_invoice_taxes(cr):
    """ Migration of account_invoice_tax object, easiest way is to call the _onchange_invoice_line_ids
        on account_invoice as it will correctly recreate the account_invoice_tax with the correct values

        Note: this will also call the recompute of some field on account_invoice (amount_untaxed, amount_untaxed_signed,
            amount_tax, amount_total, amount_total_signed, amount_total_company_signed).

            If this file is to slow to migrate, it is possible to speed it up by just recomputing the account_invoice_tax
            for all invoices that are in draft,proforma2 format. The other ones already have their account move and recomputing
            account_invoice_tax for those does not have any effect (except if user cancel invoice and then reset to draft)
    """
    env = util.env(cr)
    cr.execute("SELECT id FROM account_invoice")
    ids = map(itemgetter(0), cr.fetchall())
    invoices = util.iter_browse(env['account.invoice'], ids)
    for invoice in invoices:
        invoice._onchange_invoice_line_ids()

def migrate(cr, version):
    if not util.module_installed(cr, 'account_tax_python'):
        # This module is force installed if there are any "code" taxes. Theses taxes need the
        # module to be installed to be computed correctly. Defer the update after the
        # installation of the account_tax_python module.
        update_invoice_taxes(cr)
