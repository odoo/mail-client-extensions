# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.move_field_to_module(
        cr, "account.move.line", "intrastat_product_origin_country_id", "l10n_be_intrastat", "account_intrastat"
    )
    util.rename_xmlid(cr, *eb("{l10n_be,account}_intrastat.invoice_line_be_intrastat_data_form"))
    util.rename_xmlid(cr, *eb("{l10n_be,account}_intrastat.report_invoice_document_intrastat_2019"))
