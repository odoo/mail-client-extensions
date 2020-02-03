# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "l10n_mx_edi_cer_source", "varchar")
    util.create_column(cr, "account_move", "l10n_mx_edi_external_trade", "boolean")

    util.create_column(cr, "account_move_line", "l10n_mx_edi_tariff_fraction_id", "int4")
    util.create_column(cr, "account_move_line", "l10n_mx_edi_umt_aduana_id", "int4")
    util.create_column(cr, "account_move_line", "l10n_mx_edi_qty_umt", "int4")
    util.create_column(cr, "account_move_line", "l10n_mx_edi_price_unit_umt", "int4")

    pv = util.parse_version
    if pv(version) < pv("saas~12.4"):
        # Migrate values from account_invoice to account_move.
        # Thoses fields comes from l10n_mx_edi_external_trade which is not auto_install ...
        if util.column_exists(cr, "account_invoice", "l10n_mx_edi_cer_source"):
            cr.execute(
                """
                UPDATE account_move am
                   SET l10n_mx_edi_cer_source = inv.l10n_mx_edi_cer_source,
                       l10n_mx_edi_external_trade = inv.l10n_mx_edi_external_trade
                  FROM account_invoice inv
                 WHERE inv.move_id = am.id
                """
            )
        if util.column_exists(cr, "account_invoice", "l10n_mx_edi_tariff_fraction_id"):
            cr.execute(
                """
                UPDATE account_move_line aml
                   SET l10n_mx_edi_tariff_fraction_id = invl.l10n_mx_edi_tariff_fraction_id,
                       l10n_mx_edi_umt_aduana_id = invl.l10n_mx_edi_umt_aduana_id,
                       l10n_mx_edi_qty_umt = invl.l10n_mx_edi_qty_umt,
                       l10n_mx_edi_price_unit_umt = invl.l10n_mx_edi_price_unit_umt
                  FROM invl_aml_mapping m
                  JOIN account_invoice_line invl ON invl.id = m.invl_id
                 WHERE m.aml_id = aml.id
                 """
            )
