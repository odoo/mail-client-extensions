# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Migrate values from account_invoice to account_move.
    cr.execute(
        """
        UPDATE account_move am
           SET l10n_mx_edi_pac_status = inv.l10n_mx_edi_pac_status,
               l10n_mx_edi_sat_status = inv.l10n_mx_edi_sat_status,
               l10n_mx_edi_cfdi_name = inv.l10n_mx_edi_cfdi_name,
               l10n_mx_edi_partner_bank_id = inv.l10n_mx_edi_partner_bank_id,
               l10n_mx_edi_payment_method_id = inv.l10n_mx_edi_payment_method_id,
               l10n_mx_edi_time_invoice = inv.l10n_mx_edi_time_invoice,
               l10n_mx_edi_usage = inv.l10n_mx_edi_usage,
               l10n_mx_edi_origin = inv.l10n_mx_edi_origin
          FROM account_invoice inv
         WHERE inv.move_id = am.id
        """
    )
