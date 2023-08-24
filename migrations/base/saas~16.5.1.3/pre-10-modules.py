# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "l10n_ke_hr_payroll_bik", "l10n_ke_hr_payroll")
    util.remove_module(cr, "l10n_ae_pos")
    util.merge_module(cr, "loyalty_delivery", "sale_loyalty_delivery")
    if util.has_enterprise():
        util.merge_module(cr, "sale_timesheet_account_budget", "project_account_budget")
        util.remove_module(cr, "website_sale_renting_comparison")
        util.remove_module(cr, "website_sale_renting_wishlist")

    if util.module_installed(cr, "website_sale_digital"):
        util.move_field_to_module(cr, "ir.attachment", "product_downloadable", "website_sale_digital", "sale")

    util.remove_module(cr, "website_sale_digital")
