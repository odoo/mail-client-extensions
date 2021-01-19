# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    taxes = [util.ref(cr, "l10n_be.attn_VAT-OUT-00-EU-S"), util.ref(cr, "l10n_be.attn_VAT-OUT-00-EU-T")]
    cr.execute("UPDATE account_tax_template SET active = true WHERE id IN (%s, %s)", taxes)
