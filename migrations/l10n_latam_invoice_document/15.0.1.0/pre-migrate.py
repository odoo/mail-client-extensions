# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.move", "l10n_latam_amount_untaxed")
    util.remove_field(cr, "account.move", "l10n_latam_tax_ids")

    util.remove_field(cr, "account.move.line", "l10n_latam_price_unit")
    util.remove_field(cr, "account.move.line", "l10n_latam_price_subtotal")
    util.remove_field(cr, "account.move.line", "l10n_latam_price_net")
    util.remove_field(cr, "account.move.line", "l10n_latam_tax_ids")
