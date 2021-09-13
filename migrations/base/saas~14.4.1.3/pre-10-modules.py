# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.new_module(cr, "sale_payment_odoo", deps={"sale", "payment_odoo"}, auto_install=True)

    if util.has_enterprise():
        util.merge_module(cr, "l10n_be_hr_payroll_eco_vouchers", "l10n_be_hr_payroll")

        util.new_module(
            cr,
            "account_accountant_batch_payment",
            deps={"account_accountant", "account_batch_payment"},
            auto_install=True,
        )

        util.new_module(cr, "data_merge_helpdesk", deps={"data_merge", "helpdesk"}, auto_install=True)
        util.new_module(cr, "data_merge_project", deps={"data_merge", "project"}, auto_install=True)
        util.new_module(cr, "l10n_fr_fec_import", deps={"account_accountant", "base_vat", "l10n_fr", "l10n_fr_fec"})
        util.new_module(
            cr, "mass_mailing_sale_subscription", deps={"mass_mailing", "sale_subscription"}, auto_install=True
        )

        util.module_deps_diff(cr, "account_batch_payment", plus={"account"}, minus={"account_accountant"})
        util.module_deps_diff(cr, "account_sepa_direct_debit", plus={"account"}, minus={"account_accountant"})
        util.module_deps_diff(cr, "project_enterprise", plus={"web_enterprise"})
        util.module_deps_diff(cr, "helpdesk_sale_timesheet", plus={"helpdesk_sale"})

        util.remove_module(cr, "l10n_be_sale_intrastat")

        util.new_module(
            cr,
            "l10n_be_hr_contract_salary_group_insurance",
            deps={"l10n_be_hr_contract_salary"},
            auto_install=True,
        )
