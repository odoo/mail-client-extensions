# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Some account.user.type have been deleted from 8.0 to 9.0,
    # and they have not been handled/deleted in an upgrade script at the time.
    # odoo/odoo@6201e531088839d48fa0d66d32569d8f9c76d3e1
    # Since they now remain in databases in various version (10.0, 11.0, 12.0)
    # and they can raise an issue if they are being deleted at the end of the
    # upgrade during the ir.model.data deletion, while they are still referenced
    # by accounts, we handle them in a `0.0.0` script.
    util.delete_unused(
        cr,
        "l10n_es.account_type_capital",
        "l10n_es.account_type_inmo",
        "l10n_es.account_type_stock",
        "l10n_es.account_type_gastos_neto",
        "l10n_es.account_type_ingresos_neto",
    )
