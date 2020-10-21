# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.new_module(cr, "sale_sms", deps={"sale", "sms"}, auto_install=True)
    util.new_module(cr, "pos_coupon", deps={"coupon", "point_of_sale"})

    util.merge_module(cr, "l10n_be_invoice_bba", "l10n_be")
    util.merge_module(cr, "payment_fix_register_token", "payment")

    util.module_deps_diff(cr, "l10n_be_edi", plus={"account_edi_ubl"}, minus={"account_edi"})
    util.module_deps_diff(cr, "l10n_il", minus={"account"}, plus={"l10n_multilang"})

    if util.has_enterprise():
        util.new_module(cr, "planning_holidays", deps={"planning", "hr_holidays"}, auto_install=True)

        util.merge_module(cr, "l10n_be_hr_payroll_variable_revenue", "l10n_be_hr_payroll")  # odoo/enterprise#14458
        util.module_auto_install(cr, "crm_helpdesk", True)

        util.module_deps_diff(cr, "account_online_synchronization", plus={"account_accountant"})
        util.module_deps_diff(cr, "l10n_be_hr_payroll", plus={"hr_payroll_holidays"})

        util.remove_module(cr, "account_plaid")
        util.remove_module(cr, "account_yodlee")
        util.remove_module(cr, "account_ponto")
        util.remove_module(cr, "account_online_sync")

    util.remove_module(cr, "odoo_referral")
    util.ENVIRON['procurement_jit_uninstalled'] = not util.module_installed(cr, 'procurement_jit')
    util.remove_module(cr, "procurement_jit")
