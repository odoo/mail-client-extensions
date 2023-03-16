# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.modules_auto_discovery(
        cr, force_upgrades={"appointment_sms", "hr_work_entry_contract_attendance", "hr_work_entry_contract_planning"}
    )

    if util.has_enterprise():
        util.merge_module(cr, "documents_spreadsheet_bundle", "documents_spreadsheet")
        util.merge_module(cr, "sale_amazon_spapi", "sale_amazon")
        util.merge_module(cr, "l10n_lu_reports_annual_vat", "l10n_lu_reports")

    util.remove_module(cr, "account_accountant_check_printing")
