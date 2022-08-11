# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.update_field_references(cr, "l10n_it_country_code", "country_code", only_models=("stock.picking",))
    util.remove_field(cr, "stock.picking", "l10n_it_country_code")
