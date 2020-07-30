# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "l10n_mx_edi_pac_status", "varchar")
    util.create_column(cr, "account_move", "l10n_mx_edi_sat_status", "varchar")
    util.create_column(cr, "account_move", "l10n_mx_edi_cfdi_name", "varchar")
    util.create_column(cr, "account_move", "l10n_mx_edi_partner_bank_id", "int4")
    util.create_column(cr, "account_move", "l10n_mx_edi_payment_method_id", "int4")
    util.create_column(cr, "account_move", "l10n_mx_edi_time_invoice", "varchar")
    util.create_column(cr, "account_move", "l10n_mx_edi_usage", "varchar")
    util.create_column(cr, "account_move", "l10n_mx_edi_origin", "varchar")
