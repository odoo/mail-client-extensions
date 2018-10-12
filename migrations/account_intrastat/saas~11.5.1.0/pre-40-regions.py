# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.module_installed(cr, "l10n_be_intrastat"):
        return

    for model, module in {("res.company", "account_intrastat"), ("stock.warehouse", "stock_intrastat")}:
        # rename column before renaming field.
        # This allow keeping existing column to be kept and
        # let ORM create the new one with correct constraints
        table = util.table_of_model(cr, model)
        util.rename_column(cr, table, "region_id", "_int_region_id")
        util.rename_field(cr, model, "region_id", "intrastat_region_id")

        util.move_field_to_module(cr, model, "intrastat_transport_mode_id", "l10n_be_intrastat", module)
        cr.execute(
            """
            UPDATE ir_model_fields
               SET relation = 'account.intrastat.code'
             WHERE model = %s
               AND name = 'intrastat_region_id'
        """,
            [model],
        )
