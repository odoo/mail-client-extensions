# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Remove old reports
    util.remove_record(cr, "l10n_es_reports.mod_111")
    util.remove_record(cr, "l10n_es_reports.mod_115")
    util.remove_record(cr, "l10n_es_reports.mod_303")
