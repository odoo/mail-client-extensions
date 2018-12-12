# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module(
        cr, "account_analytic_default_hr_expense", deps={"account_analytic_default", "hr_expense"}, auto_install=True
    )
    util.new_module(cr, "hr_fleet", deps={"hr", "fleet"}, auto_install=True)
    util.new_module(cr, "hr_presence", deps={"hr", "hr_holidays", "sms"})
    util.new_module(cr, "pos_hr", deps={"point_of_sale", "hr"}, auto_install=True)

    util.rename_module(cr, "document", "attachment_indexation")

    util.module_deps_diff(cr, "base_geolocalize", plus={"base_setup"}, minus={"base"})
    util.module_deps_diff(cr, "digest", plus={"resource"})

    util.module_deps_diff(cr, "l10n_be_hr_payroll", plus={"l10n_be"})
    util.module_deps_diff(cr, "l10n_be_hr_payroll_account", minus={"l10n_be"})
    util.module_deps_diff(cr, "l10n_in_hr_payroll", plus={"l10n_in"})
    util.module_deps_diff(cr, "survey", plus={"web_tour"})

    util.merge_module(cr, "delivery_hs_code", "delivery")
    util.remove_module(cr, "crm_project")
    util.remove_module(cr, "survey_crm")
