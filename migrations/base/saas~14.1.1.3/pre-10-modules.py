# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_module(cr, "odoo_referral")
    util.new_module(cr, "sale_sms", deps={"sale", "sms"}, auto_install=True)
    util.new_module(cr, "pos_coupon", deps={"coupon", "point_of_sale"})
    util.merge_module(cr, 'payment_fix_register_token', 'payment')

    if util.has_enterprise():
        util.module_auto_install(cr, "crm_helpdesk", True)
        util.module_deps_diff(cr, "l10n_be_hr_payroll", plus={"hr_payroll_holidays"})
        util.new_module(cr, "account_online_synchronization", deps={"account_accountant"}, auto_install=True)
        util.remove_module(cr, "account_plaid")
        util.remove_module(cr, "account_yodlee")
        util.remove_module(cr, "account_ponto")
        util.remove_module(cr, "account_online_sync")
