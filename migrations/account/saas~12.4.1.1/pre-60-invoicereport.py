# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "account.invoice.report", "number", "name")
    util.rename_field(cr, "account.invoice.report", "date", "invoice_date")
    util.rename_field(cr, "account.invoice.report", "product_qty", "quantity")
    util.rename_field(cr, "account.invoice.report", "uom_name", "product_uom_id")
    util.rename_field(cr, "account.invoice.report", "payment_term_id", "invoice_payment_term_id")
    util.rename_field(cr, "account.invoice.report", "categ_id", "product_categ_id")
    util.rename_field(cr, "account.invoice.report", "user_id", "invoice_user_id")
    util.rename_field(cr, "account.invoice.report", "price_total", "price_subtotal")
    util.rename_field(cr, "account.invoice.report", "nbr", "nbr_lines")
    util.rename_field(cr, "account.invoice.report", "date_due", "invoice_date_due")
    util.rename_field(cr, "account.invoice.report", "partner_bank_id", "invoice_partner_bank_id")
    util.rename_field(cr, "account.invoice.report", "account_analytic_id", "analytic_account_id")

    util.update_field_usage(cr, "account.invoice.report", "account_line_id", "account_id")
    util.remove_field(cr, "account.invoice.report", "account_line_id")

    util.remove_field(cr, "account.invoice.report", "user_currency_price_total")
    util.remove_field(cr, "account.invoice.report", "user_currency_price_average")
    util.remove_field(cr, "account.invoice.report", "currency_rate")
    util.remove_field(cr, "account.invoice.report", "invoice_id")
    util.remove_field(cr, "account.invoice.report", "user_currency_residual")
