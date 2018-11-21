# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.module_installed(cr, "l10n_be_intrastat"):
        return

    # FIXME handle non-standard codes ?

    for table in {"res_company", "stock_warehouse"}:
        cr.execute(
            """
            UPDATE {} l
               SET intrastat_region_id = c.id
              FROM account_intrastat_code c
              JOIN l10n_be_intrastat_region t ON (t.code = c.code AND c.type='region')
             WHERE t.id = l._int_region_id
        """.format(
                table
            )
        )

        util.remove_column(cr, table, "_int_region_id")

    util.remove_model(cr, "l10n_be_intrastat.region")
