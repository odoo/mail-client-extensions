# -*- coding: utf-8 -*-
from itertools import product

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_model(cr, "l10n_pl_jpk.l10n_pl_tax_office", "l10n_pl.l10n_pl_tax_office")

    util.rename_xmlid(cr, "l10n_pl.res_partner_account_pl_jpk_form", "l10n_pl.res_partner_account_pl_form")

    if util.column_exists(cr, "account_move", "l10n_pl_delivery_date"):
        query = """
            UPDATE account_move AS move
               SET delivery_date = l10n_pl_delivery_date
              FROM res_company company
              JOIN res_country country
                ON company.account_fiscal_country_id = country.id
             WHERE company.id = move.company_id
               AND l10n_pl_delivery_date IS NOT NULL
               AND country.code = 'PL'
        """
        util.explode_execute(cr, query, "account_move", alias="move")

        util.remove_field(cr, "account.move", "l10n_pl_delivery_date")
        util.remove_field(cr, "account.move", "l10n_pl_show_delivery_date")

    util.remove_view(cr, "l10n_pl.report_invoice_document")

    renames = """
        kraj_{3_lub_,}5
        kraj_{7_lub_,}8
        kraj_{22_lub_,}23
    """
    for xid in util.splitlines(renames):
        for prefix, suffix in product(("", "podatek_"), ("", "_tag")):
            from_, to = util.expand_braces(f"l10n_pl.account_tax_report_line_{prefix}{xid}{suffix}")
            util.rename_xmlid(cr, from_, to)
