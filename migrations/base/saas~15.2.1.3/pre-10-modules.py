# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if util.has_enterprise():
        # merges
        util.merge_module(cr, "website_helpdesk_form", "website_helpdesk")
        util.merge_module(cr, "l10n_be_hr_payroll_canteen", "l10n_be_hr_contract_salary")
        util.merge_module(cr, "l10n_be_hr_payroll_december", "l10n_be_hr_payroll")
        util.merge_module(cr, "l10n_be_hr_payroll_holiday_pay_recovery", "l10n_be_hr_payroll")
        util.merge_module(cr, "l10n_be_hr_payroll_report_measures", "l10n_be_hr_payroll")
        util.merge_module(cr, "l10n_be_hr_contract_salary_group_insurance", "l10n_be_hr_payroll")

    util.merge_module(cr, "base_address_city", "base_address_extended")

    util.remove_module(cr, "l10n_be_reports_base_address_extended")

    util.modules_auto_discovery(cr)

    if util.has_enterprise():
        util.force_upgrade_of_fresh_module(cr, "appointment_hr")
