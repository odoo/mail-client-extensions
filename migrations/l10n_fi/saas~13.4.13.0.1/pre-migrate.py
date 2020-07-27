# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "l10n_fi.tax_report_vat_relief", "l10n_fi.vat_report_relief")
