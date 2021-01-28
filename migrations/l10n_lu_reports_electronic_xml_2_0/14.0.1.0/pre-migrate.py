# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "l10n_lu.generate.tax.report", "l10n_lu_annex_warning_visible")
