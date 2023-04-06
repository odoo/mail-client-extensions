# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.update_field_usage(cr, "account.move", "l10n_latam_country_code", "country_code")
    util.remove_field(cr, "account.move", "l10n_latam_country_code")
