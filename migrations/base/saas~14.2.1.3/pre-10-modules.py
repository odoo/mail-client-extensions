# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "l10n_se_ocr", "l10n_se")
    util.merge_module(cr, "sale_timesheet_edit", "sale_timesheet", without_deps=True)

    util.module_deps_diff(cr, "crm", plus={"web_kanban_gauge"})
    util.module_deps_diff(cr, "website_mass_mailing", plus={"google_recaptcha"})

    if util.has_enterprise():
        util.merge_module(cr, "helpdesk_sale_timesheet_edit", "helpdesk_sale_timesheet", without_deps=True)
        util.merge_module(cr, "website_crm_score", "crm", without_deps=True)

        util.new_module(cr, "helpdesk_fsm_report", deps={"helpdesk_fsm", "industry_fsm_report"}, auto_install=True)
        util.new_module(
            cr,
            "helpdesk_fsm_sale",
            deps={"helpdesk_fsm", "helpdesk_sale_timesheet", "industry_fsm_sale"},
            auto_install=True,
        )
        util.new_module(
            cr, "hr_contract_salary_holidays", deps={"hr_contract_salary", "hr_holidays"}, auto_install=True
        )
        util.new_module(cr, "l10n_us_payment_nacha", deps={"account_batch_payment", "l10n_us"}, auto_install=True)
        util.new_module(cr, "l10n_be_hr_payroll_eco_vouchers", deps={"l10n_be_hr_payroll"}, auto_install=True)
