# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.update_field_usage(cr, "stock.picking", "l10n_it_country_code", "country_code")
    util.remove_field(cr, "stock.picking", "l10n_it_country_code")
