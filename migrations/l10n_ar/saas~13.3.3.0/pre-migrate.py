# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.update_field_references(cr, "l10n_ar_country_code", "country_code")
    util.remove_field(cr, "res.company", "l10n_ar_country_code")
