# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_mx_edi_extended.cfdiv33_extended")
    util.remove_view(cr, "l10n_mx_edi_extended.view_l10n_mx_edi_invoice_form_inherit_40")
    util.remove_view(cr, "l10n_mx_edi_extended.l10n_mx_edi_40_payment20_extended")
