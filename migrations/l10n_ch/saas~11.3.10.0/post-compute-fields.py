# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("SELECT id FROM res_partner_bank WHERE l10n_ch_postal IS NULL")
    ids = [b[0] for b in cr.fetchall()]
    util.recompute_fields(cr, "res.partner.bank", ["l10n_ch_postal"], ids=ids)
