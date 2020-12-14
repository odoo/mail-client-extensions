# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    taxes = [util.ref(cr, "l10n_lu.lu_2011_tax_VB-IC-0"), util.ref(cr, "l10n_lu.lu_2015_tax_VB-TR-0")]
    cr.execute("UPDATE account_tax_template SET active = true WHERE id IN (%s, %s)", taxes)
