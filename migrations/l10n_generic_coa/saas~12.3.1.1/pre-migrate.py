# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.force_noupdate(cr, "l10n_generic_coa.sale_tax_template", noupdate=False)
    util.force_noupdate(cr, "l10n_generic_coa.purchase_tax_template", noupdate=False)
