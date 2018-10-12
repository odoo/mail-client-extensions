# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.module_installed(cr, "l10n_be_intrastat"):
        return

    # FIXME handle non-standard codes ?

    cr.execute(
        """
        UPDATE account_invoice_line l
           SET intrastat_transaction_id = c.id
          FROM account_intrastat_code c
          JOIN l10n_be_intrastat_transaction t ON (t.code = c.code AND c.type='transaction')
         WHERE t.id = l._int_trans_id
    """
    )

    util.remove_column(cr, "account_invoice_line", "_int_trans_id")

    util.remove_model(cr, "l10n_be_intrastat.transaction")
