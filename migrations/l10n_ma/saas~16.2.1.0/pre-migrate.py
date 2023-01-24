# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "l10n_ma.l10n_kzc_temp_chart", "l10n_ma.l10n_ma_chart_template")
