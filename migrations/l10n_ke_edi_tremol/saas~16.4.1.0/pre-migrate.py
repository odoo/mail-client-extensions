# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_ke_edi_tremol.l10n_ke_inherit_product_product_form_view")
    util.remove_view(cr, "l10n_ke_edi_tremol.l10n_ke_inherit_product_template_form_view")
