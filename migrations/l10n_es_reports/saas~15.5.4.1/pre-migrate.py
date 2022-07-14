# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    for model in (
        "l10n_es_reports.aeat.report.wizard",
        "l10n_es_reports.mod111.wizard",
        "l10n_es_reports.mod115.wizard",
        "l10n_es_reports.mod303.wizard",
    ):
        util.remove_model(cr, model)
