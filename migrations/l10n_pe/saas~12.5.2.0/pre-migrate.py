# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    for model in ["account.tax.report.line", "account.tax.template", "account.account.template"]:
        cr.execute(
            """
            SELECT name
              FROM ir_model_data
             WHERE module = 'l10n_pe'
               AND model=%s
        """,
            [model],
        )
        for name in cr.fetchall():
            util.remove_record(cr, "l10n_pe." + name[0])

    cr.execute(
        """
        SELECT name
          FROM ir_model_data
         WHERE module = 'l10n_pe'
           AND model IN ('account.tax.group', 'account.account.type')
    """,
    )
    util.delete_unused(cr, *["l10n_pe." + name for name, in cr.fetchall()])

    util.remove_record(cr, "l10n_pe.pe_chart_template")  # recreate it.
