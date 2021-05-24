# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_latam_invoice_document.external_layout_{clean,bold}"))
    util.rename_xmlid(cr, *eb("l10n_latam_invoice_document.external_layout_{background,striped}"))

    util.remove_view(cr, "l10n_latam_invoice_document.sequence_view")
    util.remove_view(cr, "l10n_latam_invoice_document.sequence_view_tree")
    util.remove_view(cr, "l10n_latam_invoice_document.view_sequence_search")

    util.remove_field(cr, "ir.sequence", "l10n_latam_document_type_id")
