# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.module_deps_diff(cr, "event", plus={"utm"})
    util.module_deps_diff(cr, "link_tracker", plus={"mail"})
    util.new_module(cr, "mrp_landed_costs", deps={"stock_landed_costs", "mrp"}, auto_install=True)
    util.module_deps_diff(cr, "sale_coupon", plus={"sale"}, minus={"sale_management"})
    util.remove_module(cr, "social_linkedin_company_support")

    if util.has_enterprise():
        util.new_module(cr, "hr_contract_salary_payroll", deps={"hr_contract_salary", "hr_payroll"}, auto_install=True)
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
