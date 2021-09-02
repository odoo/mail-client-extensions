# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module(
        cr, "account_analytic_default_hr_expense", deps={"account_analytic_default", "hr_expense"}, auto_install=True
    )
    util.new_module(cr, "hr_fleet", deps={"hr", "fleet"}, auto_install=True)
    util.new_module(cr, "hr_presence", deps={"hr", "hr_holidays", "sms"})
    util.new_module(cr, "l10n_in_pos", deps={"l10n_in", "point_of_sale"}, auto_install=True)
    util.new_module(cr, "pos_hr", deps={"point_of_sale", "hr"}, auto_install=True)

    util.rename_module(cr, "document", "attachment_indexation")

    util.module_deps_diff(cr, "base_geolocalize", plus={"base_setup"}, minus={"base"})
    util.module_deps_diff(cr, "digest", plus={"resource"})

    if not util.version_gte("saas~12.3"):
        # The dependence is removed in saas~12.3
        # Avoid adding it transiently, as it will have the side effect of force-installing the `account` module
        util.module_deps_diff(cr, "l10n_be_hr_payroll", plus={"l10n_be"})

    util.module_deps_diff(cr, "l10n_be_hr_payroll_account", minus={"l10n_be"})
    util.module_deps_diff(cr, "l10n_in_hr_payroll", plus={"l10n_in"})
    util.module_deps_diff(cr, "survey", plus={"web_tour"})

    util.merge_module(cr, "delivery_hs_code", "delivery")
    util.remove_module(cr, "crm_project")
    util.remove_module(cr, "survey_crm")
    util.force_migration_of_fresh_module(cr, "pos_hr")

    if util.has_enterprise():
        util.new_module(cr, "crm_helpdesk", deps={"crm", "helpdesk"})
        util.new_module(cr, "im_livechat_enterprise", deps={"im_livechat", "web_dashboard"}, auto_install=True)
        util.new_module(
            cr, "test_l10n_be_hr_payroll_account", deps={"hr_contract_salary", "l10n_be_hr_payroll_account"}
        )
        util.new_module(cr, "voip_crm", deps={"base", "crm", "voip"}, auto_install=True)

        util.module_deps_diff(cr, "documents", plus={"attachment_indexation"})
        util.module_deps_diff(cr, "ocn_client", plus={"web_mobile"})

        util.merge_module(cr, "l10n_mx_edi_payment", "l10n_mx_edi")
