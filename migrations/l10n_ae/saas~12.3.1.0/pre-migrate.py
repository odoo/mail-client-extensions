# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_record(cr, "l10n_ae.sale_tax_template")
    util.remove_record(cr, "l10n_ae.purchase_tax_template")
