# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "l10n_cl_account_invoice_reference", "l10n_cl_reference_doc_type_id", "int4")

    cr.execute(
        """
        UPDATE l10n_cl_account_invoice_reference lcair
        SET l10n_cl_reference_doc_type_id = lldt.id
        FROM l10n_latam_document_type lldt
        JOIN res_country c ON c.id = lldt.country_id
        WHERE lldt.code = lcair.l10n_cl_reference_doc_type_selection AND c.code = 'CL'
    """
    )

    util.remove_field(cr, "l10n_cl.account.invoice.reference", "l10n_cl_reference_doc_type_selection")
