# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "l10n_latam_document_type", "l10n_cl_active", "boolean")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_cl{_edi_stock,}.dc_gd"))
    util.rename_xmlid(cr, *eb("l10n_cl{_edi_stock,}.dc_gd_dte"))
