# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # l10n_mx cfid 3.0 and 4.0 merge
    util.remove_view(cr, "l10n_mx_edi_stock.cfdi_cartaporte_40")
