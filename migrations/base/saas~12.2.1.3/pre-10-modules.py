# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module(cr, "crm_iap_lead", deps={"crm", "iap"})
    util.new_module(cr, "hr_attendance_presence", deps={"hr_attendance", "hr_presence"}, auto_install=True)
    util.new_module(cr, "hr_skills", deps={"hr"})
    util.new_module(cr, "l10n_ie", deps={"account", "base_iban", "base_vat"})
    util.new_module(cr, "payment_payulatam", deps={"payment"})
    util.new_module(
        cr, "purchase_requisition_stock", deps={"purchase_requisition", "purchase_stock"}, auto_install=True
    )
    util.new_module(cr, "website_profile", deps={"gamification", "website_partner"})
    util.new_module(cr, "website_sale_slides", deps={"website_sale", "website_slides"}, auto_install=True)
    util.new_module(cr, "website_slides_forum", deps={"website_slides", "website_forum"}, auto_install=True)
    util.new_module(cr, "website_slides_survey", deps={"website_slides", "website_survey"}, auto_install=True)

    util.module_deps_diff(cr, "crm_reveal", plus={"crm_iap_lead"})
    util.rename_module(cr, "crm_reveal", "crm_iap_lead_website")
    util.force_migration_of_fresh_module(cr, "crm_iap_lead")
    util.module_deps_diff(cr, "event", plus={"portal"})
    util.module_deps_diff(cr, "portal", plus={"web", "web_editor"})
    util.module_deps_diff(cr, "purchase_requisition", plus={"purchase"}, minus={"purchase_stock"})
    util.module_deps_diff(cr, "survey", plus={"auth_signup"})
    util.module_deps_diff(cr, "website_forum", plus={"website_profile"}, minus={"gamification", "website_partner"})
    util.module_deps_diff(cr, "website_slides", plus={"website_profile", "website_rating"})

    util.force_migration_of_fresh_module(cr, "website_profile")

    if util.modules_installed(cr, "hr_payroll", "account"):
        util.force_install_module(cr, "hr_payroll_account")

    if util.modules_installed(cr, "hr_payroll", "l10n_be"):
        util.force_install_module(cr, "l10n_be_hr_payroll")

    if util.has_enterprise():
        util.rename_module(cr, "quality_mrp_iot", "mrp_workorder_iot")
        util.rename_module(cr, "timesheet_grid_sale", "sale_timesheet_enterprise")

        util.new_module(cr, "sale_project_timesheet_enterprise", deps={"sale_timesheet_enterprise"})
        util.new_module(cr, "approvals", deps={"mail", "hr"})
        util.new_module(cr, "industry_fsm", deps={"project_enterprise", "sale_project_timesheet_enterprise"})
        util.new_module(cr, "industry_fsm_report", deps={"project", "web_studio", "industry_fsm"})
        util.new_module(cr, "hr_documents", deps={"documents", "hr"}, auto_install=True)
        util.new_module(cr, "quality_control_iot", deps={"quality_control", "iot"}, auto_install=True)
        util.new_module(cr, "quality_mrp_workorder_iot", deps={"quality_mrp_workorder", "iot"}, auto_install=True)

        util.module_deps_diff(cr, "account_invoice_extract", plus={"account"}, minus={"account_accountant"})
        util.module_deps_diff(cr, "documents_account", plus={"account_reports"}, minus={"account"})
        util.module_deps_diff(cr, "mrp_workorder_iot", plus={"mrp_workorder"}, minus={"quality_mrp_workorder"})
        util.module_deps_diff(cr, "quality_iot", minus={"quality_control"}, plus={"quality"})

    cr.execute("DELETE FROM ir_translation WHERE lang = 'fil' ")
    cr.execute("UPDATE res_lang set code = 'fil_PH', iso_code = 'fil' where code ilike 'fil%' ")
    cr.execute("UPDATE res_partner set lang = 'fil_PH' where lang = 'fil' ")
