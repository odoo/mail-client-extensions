# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # this report is completely restructured in 16.5
    util.remove_record(cr, "l10n_lu.tax_report")
