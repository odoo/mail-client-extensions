# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.module_installed(cr, "l10n_be_intrastat"):
        return

    # Move data from l10n_be_intrastat.transaction to account.intrastat.code with type=transaction
    util.rename_column(cr, "account_invoice_line", "intrastat_transaction_id", "_int_trans_id")

    util.move_field_to_module(
        cr, "account.invoice.line", "intrastat_transaction_id", "l10n_be_intrastat", "account_intrastat"
    )
    cr.execute(
        """
        UPDATE ir_model_fields
           SET relation = 'account.intrastat.code'
         WHERE model = 'account.invoice.line'
           AND name = 'intrastat_transaction_id'
    """
    )
