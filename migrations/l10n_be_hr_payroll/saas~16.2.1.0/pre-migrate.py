# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "l10n_be_eco_vouchers_wizard", "reference_year")
