# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "l10n_cl_report_tasa_ppm", "float8")
    util.create_column(cr, "res_company", "l10n_cl_report_fpp_value", "float8")
