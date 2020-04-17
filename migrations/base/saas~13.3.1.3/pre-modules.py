# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.module_deps_diff(cr, "event", plus={"utm"})
    util.module_deps_diff(cr, "link_tracker", plus={"mail"})
    util.new_module(cr, "mrp_landed_costs", deps={"stock_landed_costs", "mrp"}, auto_install=True)
    util.new_module(cr, "account_qr_code_sepa", deps={"account", "base_iban"}, auto_install=True)
    util.module_deps_diff(cr, "sale_coupon", plus={"sale"}, minus={"sale_management"})

    util.module_auto_install(cr, "crm_iap_lead", True)
    util.module_auto_install(cr, "crm_iap_lead_enrich", True)

    if util.has_enterprise():
        util.new_module(
            cr, "documents_l10n_be_hr_payroll", deps={"documents_hr_payroll", "l10n_be_hr_payroll"}, auto_install=True
        )
        util.new_module(cr, "hr_contract_salary_payroll", deps={"hr_contract_salary", "hr_payroll"}, auto_install=True)
        util.new_module(
            cr, "purchase_stock_enterprise", deps={"purchase_enterprise", "purchase_stock"}, auto_install=True
        )
        util.new_module(cr, "sale_renting_crm", deps={"sale_renting", "crm"}, auto_install=True)

        util.new_module(
            cr,
            "l10n_be_hr_contract_salary",
            deps={"hr_contract_salary_payroll", "l10n_be_hr_payroll_fleet"},
            auto_install=True,
        )
        util.module_deps_diff(
            cr,
            "hr_contract_salary",
            plus={"hr_contract_reports", "http_routing"},
            minus={"website", "l10n_be_hr_payroll_fleet"},
        )
        util.module_deps_diff(
            cr,
            "test_l10n_be_hr_payroll_account",
            plus={"hr_contract_salary_payroll", "l10n_be_hr_contract_salary"},
            minus={"hr_contract_salary"},
        )

        util.merge_module(cr, "social_linkedin_company_support", "social_linkedin")
