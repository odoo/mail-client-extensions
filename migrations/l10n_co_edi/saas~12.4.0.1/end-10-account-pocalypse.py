# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Migrate values from account_invoice to account_move.
    cr.execute(
        """
        UPDATE account_move am
        SET l10n_co_edi_datetime_invoice = inv.l10n_co_edi_datetime_invoice,
            l10n_co_edi_type = inv.l10n_co_edi_type,
            l10n_co_edi_transaction = inv.l10n_co_edi_transaction,
            l10n_co_edi_invoice_name = inv.l10n_co_edi_invoice_name,
            l10n_co_edi_invoice_status = inv.l10n_co_edi_invoice_status,
            l10n_co_edi_attachment_url = inv.l10n_co_edi_attachment_url
        FROM account_invoice inv
        WHERE inv.move_id = am.id
    """
    )
