# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "l10n_latam_identification_type", "l10n_co_document_code", "varchar")
    util.remove_view(cr, "l10n_co.view_partner_form_inherit_l10n_co")
