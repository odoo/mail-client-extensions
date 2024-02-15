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
    util.create_column(cr, "account_move", "incoterm_location", "varchar")

    if util.module_installed(cr, "l10n_sa"):
        util.move_field_to_module(cr, "account.move", "l10n_sa_delivery_date", "l10n_sa", "account")
        util.rename_field(cr, "account.move", "l10n_sa_delivery_date", "delivery_date")
        util.move_field_to_module(cr, "account.move", "l10n_sa_show_delivery_date", "l10n_sa", "account")
        util.rename_field(cr, "account.move", "l10n_sa_show_delivery_date", "show_delivery_date")
    else:
        util.create_column(cr, "account_move", "delivery_date", "date")

    util.remove_constraint(cr, "account_tax", "account_tax_name_company_uniq")
    util.remove_constraint(cr, "account_account", "account_account_code_company_uniq")
