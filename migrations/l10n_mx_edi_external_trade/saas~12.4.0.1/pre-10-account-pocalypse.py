# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "l10n_mx_edi_cer_source", "varchar")
    util.create_column(cr, "account_move", "l10n_mx_edi_external_trade", "boolean")

    util.create_column(cr, "account_move_line", "l10n_mx_edi_tariff_fraction_id", "int4")
    util.create_column(cr, "account_move_line", "l10n_mx_edi_umt_aduana_id", "int4")
    util.create_column(cr, "account_move_line", "l10n_mx_edi_qty_umt", "numeric")
    util.create_column(cr, "account_move_line", "l10n_mx_edi_price_unit_umt", "double precision")
