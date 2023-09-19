# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "l10n_ke_hr_payroll_bik", "l10n_ke_hr_payroll")
    util.remove_module(cr, "l10n_ae_pos")
    util.remove_module(cr, "purchase_enterprise")
    util.merge_module(cr, "loyalty_delivery", "sale_loyalty_delivery")
    if util.has_enterprise():
        util.merge_module(cr, "sale_timesheet_account_budget", "project_account_budget")
        util.remove_module(cr, "website_sale_renting_comparison")
        util.remove_module(cr, "website_sale_renting_wishlist")
        util.merge_module(cr, "l10n_pl_reports_jpk", "l10n_pl_reports")
        util.remove_module(cr, "l10n_br_avatax_sale")
        util.rename_module(cr, "account_avatax_sale_subscription", "sale_subscription_external_tax")
        util.rename_module(cr, "website_sale_account_avatax", "website_sale_external_tax")

    if util.module_installed(cr, "website_sale_digital"):
        util.move_field_to_module(cr, "ir.attachment", "product_downloadable", "website_sale_digital", "sale")

    util.remove_module(cr, "website_sale_digital")
    util.merge_module(cr, "l10n_it_edi_pa", "l10n_it_edi")

    util.remove_module(cr, "sale_quotation_builder")
    util.merge_module(cr, "event_barcode", "event")
    util.merge_module(cr, "l10n_pl_jpk", "l10n_pl")
    util.remove_module(cr, "l10n_pl_sale_stock")

    if util.has_enterprise():
        util.merge_module(cr, "account_sepa_pain_001_001_09", "account_sepa")
        util.merge_module(cr, "hr_payroll_account_sepa_09", "hr_payroll_account_sepa")
        util.merge_module(cr, "l10n_lu_reports_annual_vat_2023", "l10n_lu_reports")
