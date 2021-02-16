# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "account_edi_extended", "account_edi", without_deps=True)

    if util.has_enterprise():

        util.merge_module(cr, "l10n_be_hr_payroll_273S_274", "l10n_be_hr_payroll")
        util.merge_module(cr, "l10n_be_hr_payroll_273S_274_account", "l10n_be_hr_payroll_account")
        util.merge_module(cr, "documents_l10n_be_hr_payroll_273S_274", "documents_l10n_be_hr_payroll")
        util.merge_module(cr, "l10n_be_hr_payroll_impulsion", "l10n_be_hr_payroll")
