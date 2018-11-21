# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.module_installed(cr, "l10n_be_intrastat"):
        return

    # Move data from l10n_be_intrastat.transport_mode to account.intrastat.code with type=transport

    for model in {"account.invoice", "res.company"}:
        # rename column before renaming field.
        # This allow keeping existing column to be kept and
        # let ORM create the new one with correct constraints
        table = util.table_of_model(cr, model)
        util.rename_column(cr, table, "transport_mode_id", "_int_transp_id")
        util.rename_field(cr, model, "transport_mode_id", "intrastat_transport_mode_id")

        util.move_field_to_module(cr, model, "intrastat_transport_mode_id", "l10n_be_intrastat", "account_intrastat")
        cr.execute(
            """
            UPDATE ir_model_fields
               SET relation = 'account.intrastat.code'
             WHERE model = %s
               AND name = 'intrastat_transport_mode_id'
        """,
            [model],
        )
