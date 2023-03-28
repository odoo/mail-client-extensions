# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "account.move", "l10n_de_addresses", "l10n_de", "l10n_din5008")
    util.rename_field(cr, "account.move", "l10n_de_addresses", "l10n_din5008_addresses")
