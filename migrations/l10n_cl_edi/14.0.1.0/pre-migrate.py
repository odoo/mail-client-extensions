# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "ir.sequence", "l10n_latam_document_type_code")
    util.remove_field(cr, "ir.sequence", "l10n_cl_dte_caf_ids")
    util.remove_field(cr, "ir.sequence", "l10n_cl_qty_available")

    util.remove_field(cr, "l10n_cl.dte.caf", "sequence_id")

    util.remove_field(cr, "res.config.settings", "l10n_cl_country_code")

    util.remove_record(cr, "l10n_cl_edi.access_ir_sequence_caf_manager")
    util.remove_record(cr, "l10n_cl_edi.caf_per_company")
    util.remove_record(cr, "l10n_cl_edi.signature_certificate_per_company")

    util.remove_view(cr, "l10n_cl_edi.sequence_view")
    util.remove_view(cr, "l10n_cl_edi.barcode_stamp_footer_with_payments")
