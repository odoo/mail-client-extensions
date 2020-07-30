# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "l10n_es_reports_mod347_invoice_type", "varchar")
    util.create_column(cr, "account_move", "l10n_es_reports_mod349_invoice_type", "varchar")
    util.create_column(cr, "account_move", "l10n_es_reports_mod349_available", "boolean")
