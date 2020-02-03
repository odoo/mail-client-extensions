# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_at.account_reports_at_statements_menu")
    util.delete_unused(cr, "account_account_type", ["l10n_at.account_type_other"])

    for model in [
        "account.fiscal.position.tax.template",
        "account.fiscal.position.account.template",
        "account.fiscal.position.template",
        "account.tax.template",
        "account.tax.report.line",
        "account.account.template",
    ]:
        cr.execute(
            """
            SELECT name
              FROM ir_model_data
             WHERE module = 'l10n_at'
               AND model=%s
        """,
            [model],
        )
        for name in cr.fetchall():
            util.remove_record(cr, "l10n_at." + name[0])

    util.remove_record(cr, "l10n_at.austria_chart_template")
