# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "web_kanban_gauge", "web")
    util.merge_module(cr, "pos_epson_printer_restaurant", "pos_epson_printer")
    if util.has_enterprise():
        util.merge_module(cr, "pos_restaurant_iot", "pos_iot")
        util.merge_module(cr, "l10n_hk_hr_payroll_hsbc_autopay", "l10n_hk_hr_payroll")

    # l10n_mx cfid 3.0 and 4.0 merge
    util.merge_module(cr, "l10n_mx_edi_stock_extended_40", "l10n_mx_edi_stock_extended")
    util.merge_module(cr, "l10n_mx_edi_stock_40", "l10n_mx_edi_stock")
    util.merge_module(cr, "l10n_mx_edi_extended_40", "l10n_mx_edi_extended")
    util.merge_module(cr, "l10n_mx_edi_40", "l10n_mx_edi")
    util.merge_module(cr, "l10n_pe_edi_stock_20", "l10n_pe_edi_stock")
    util.merge_module(cr, "website_event_questions", "website_event")
    util.merge_module(cr, "website_event_crm_questions", "website_event_crm")
