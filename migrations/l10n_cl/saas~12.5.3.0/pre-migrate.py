# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    for model in ["account.tax.report.line", "account.tax.template", "account.account.template"]:
        cr.execute(
            """
            SELECT name
              FROM ir_model_data
             WHERE module = 'l10n_cl'
               AND model=%s
        """,
            [model],
        )
        for name in cr.fetchall():
            util.remove_record(cr, "l10n_cl." + name[0])

    util.delete_unused(cr, "account_account_type", ["l10n_cl.account_account_type_NCLASIFICADO"])
    util.remove_record(cr, "l10n_cl.cl_chart_template")
