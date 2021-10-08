# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "l10n_pe_edi.tax_group_icbper", "l10n_pe.tax_group_icbper")
