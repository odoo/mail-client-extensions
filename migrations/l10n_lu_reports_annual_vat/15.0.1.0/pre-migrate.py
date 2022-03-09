# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "l10n_lu.yearly.tax.report.manual", "by_fidu")
