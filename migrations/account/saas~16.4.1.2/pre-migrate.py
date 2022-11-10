# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Onboardings move
    util.remove_view(cr, "account.account_invoice_onboarding_panel")
    util.remove_view(cr, "account.account_invoice_onboarding_sale_tax_form")
    util.remove_view(cr, "account.onboarding_invoice_layout_step")
    util.remove_view(cr, "account.onboarding_create_invoice_step")
    util.remove_view(cr, "account.onboarding_bank_account_step")
    util.remove_view(cr, "account.onboarding_fiscal_year_step")
    util.remove_view(cr, "account.onboarding_chart_of_account_step")
    util.remove_view(cr, "account.onboarding_taxes_step")
    util.remove_view(cr, "account.account_dashboard_onboarding_panel")
    util.remove_view(cr, "account.onboarding_sale_tax_step")

    util.remove_record(cr, "account.action_open_account_onboarding_create_invoice")
