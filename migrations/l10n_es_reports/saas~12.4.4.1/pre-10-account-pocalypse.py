# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "l10n_es_reports_mod347_invoice_type", "varchar")
    util.create_column(cr, "account_move", "l10n_es_reports_mod349_invoice_type", "varchar")
    util.create_column(cr, "account_move", "l10n_es_reports_mod349_available", "boolean")

    # Migrate values from account_invoice to account_move.

    cr.execute(
        """
        UPDATE account_move am
        SET l10n_es_reports_mod347_invoice_type = inv.l10n_es_reports_mod347_invoice_type,
            l10n_es_reports_mod349_invoice_type = inv.l10n_es_reports_mod349_invoice_type,
            l10n_es_reports_mod349_available = inv.l10n_es_reports_mod349_available
        FROM account_invoice inv
        WHERE inv.move_id = am.id
    """
    )
