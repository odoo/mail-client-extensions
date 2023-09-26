# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_mx_edi_website_sale.wizard_checkout_inherit_l10n_mx_edi")
    util.remove_view(cr, "l10n_mx_edi_website_sale.l10n_mx_edi_extra_info")
    util.remove_view(cr, "l10n_mx_edi_website_sale.l10n_mx_edi_checkout")
