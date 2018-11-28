# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "account.tax", "cash_basis_account", "cash_basis_account_id")
    util.rename_field(cr, "account.tax.template", "cash_basis_account", "cash_basis_account_id")

    util.remove_field(cr, "account.register.payment", "company_id")
    # now a non-stored related
    util.remove_column(cr, "account_payment", "company_id")

    util.remove_view(cr, "account.view_account_invoice_filter_inherit_invoices")
    util.remove_view(cr, "account.view_account_invoice_filter_inherit_credit_notes")
    util.remove_view(cr, "account.view_tax_form_cash_basis_inherit")  # from account_cash_basis_base_account module
