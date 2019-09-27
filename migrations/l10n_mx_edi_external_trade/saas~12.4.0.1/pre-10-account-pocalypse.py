# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'account_move', 'l10n_mx_edi_cer_source', 'varchar')
    util.create_column(cr, 'account_move', 'l10n_mx_edi_external_trade', 'varchar')

    util.create_column(cr, 'account_move_line', 'l10n_mx_edi_tariff_fraction_id', 'int4')
    util.create_column(cr, 'account_move_line', 'l10n_mx_edi_umt_aduana_id', 'int4')
    util.create_column(cr, 'account_move_line', 'l10n_mx_edi_qty_umt', 'int4')
    util.create_column(cr, 'account_move_line', 'l10n_mx_edi_price_unit_umt', 'int4')

    # Migrate values from account_invoice to account_move.
    cr.execute('''
        UPDATE account_move am
        SET l10n_mx_edi_cer_source = inv.l10n_mx_edi_cer_source,
            l10n_mx_edi_external_trade = inv.l10n_mx_edi_external_trade
        FROM account_invoice inv
        WHERE inv.move_id = am.id;

        UPDATE account_move_line aml
        SET l10n_mx_edi_tariff_fraction_id = invl.l10n_mx_edi_tariff_fraction_id,
            l10n_mx_edi_umt_aduana_id = invl.l10n_mx_edi_umt_aduana_id,
            l10n_mx_edi_qty_umt = invl.l10n_mx_edi_qty_umt,
            l10n_mx_edi_price_unit_umt = invl.l10n_mx_edi_price_unit_umt
        FROM account_invoice_line invl
        JOIN invl_aml_mapping mapping ON mapping.invl_id = invl.id
        WHERE mapping.is_invoice_line IS TRUE
    ''')
