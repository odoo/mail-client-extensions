# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.new_module(cr, "sale_sms", deps={"sale", "sms"}, auto_install=True)
    util.new_module(cr, "pos_coupon", deps={"coupon", "point_of_sale"})

    util.merge_module(cr, "l10n_be_invoice_bba", "l10n_be")
    util.merge_module(cr, "payment_fix_register_token", "payment")

    util.module_deps_diff(cr, "l10n_be_edi", plus={"account_edi_ubl"}, minus={"account_edi"})
    util.module_deps_diff(cr, "l10n_il", minus={"account"}, plus={"l10n_multilang"})

    util.rename_module(cr, "website_event_track_exhibitor", "website_event_exhibitor")
    if not util.module_installed(cr, "website_event_exhibitor"):
        # If website_event_track is installed (defining event_sponsor) and has
        # any data, force installation of website_event_exhibitor that is the
        # new module holding sponsor management
        if util.table_exists(cr, "event_sponsor"):
            cr.execute("SELECT count(*) FROM event_sponsor")
            if cr.fetchone()[0]:
                util.force_install_module(cr, "website_event_exhibitor")
                util.force_migration_of_fresh_module(cr, "website_event_exhibitor")
    util.module_deps_diff(cr, "website_event_exhibitor", plus={"website_event"}, minus={"website_event_track"})

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
    util.ENVIRON["procurement_jit_uninstalled"] = not util.module_installed(cr, "procurement_jit")
    util.remove_module(cr, "procurement_jit")
