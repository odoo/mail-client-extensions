# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.module_installed(cr, "l10n_be_intrastat"):
        return

    # FIXME handle non-standard codes ?

    for table in {"account_invoice", "res_company"}:
        cr.execute(
            """
            UPDATE {} l
               SET intrastat_transport_mode_id = c.id
              FROM account_intrastat_code c
              JOIN l10n_be_intrastat_transport_mode t ON (t.code = c.code AND c.type='transport')
             WHERE t.id = l._int_transp_id
        """.format(
                table
            )
        )

        util.remove_column(cr, table, "_int_transp_id")

    util.remove_model(cr, "l10n_be_intrastat.transport_mode")
