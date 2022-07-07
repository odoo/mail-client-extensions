# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    # As l10n_pe depends l10n_latam_invoice_document instead of l10n_pe_edi now,
    # the xml records for document types should be defined in l10n_pe already.
    for t in ["01", "02", "07", "07b", "08", "08b", "20", "40"]:
        util.rename_xmlid(cr, f"l10n_pe_edi.document_type{t}", f"l10n_pe.document_type{t}")
