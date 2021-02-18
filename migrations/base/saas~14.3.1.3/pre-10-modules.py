# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "account_edi_extended", "account_edi", without_deps=True)

    util.new_module(cr, "gift_card", deps={"sale"})
    util.new_module(cr, "website_sale_gift_card", deps={"website_sale", "gift_card"})

    util.module_deps_diff(cr, "l10n_pe", plus={"l10n_latam_invoice_document", "account_debit_note"})

    if util.has_enterprise():
        util.merge_module(cr, "l10n_be_hr_payroll_273S_274", "l10n_be_hr_payroll")
        util.merge_module(cr, "l10n_be_hr_payroll_273S_274_account", "l10n_be_hr_payroll_account")
        util.merge_module(cr, "documents_l10n_be_hr_payroll_273S_274", "documents_l10n_be_hr_payroll")
        util.merge_module(cr, "l10n_be_hr_payroll_impulsion", "l10n_be_hr_payroll")

        util.module_deps_diff(
            cr,
            "l10n_pe_edi",
            plus={"account_edi"},
            minus={"l10n_latam_invoice_document", "account_debit_note", "account_edi_extended"},
        )
