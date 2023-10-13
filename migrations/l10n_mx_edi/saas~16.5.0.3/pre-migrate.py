# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "l10n_mx_edi_certificate", "company_id", "integer")
    cr.execute(
        """
            WITH info AS (
                SELECT l10n_mx_edi_certificate_id as certificate_id,
                       array_agg(res_company_id) AS company_ids
                  FROM l10n_mx_edi_certificate_res_company_rel
              GROUP BY certificate_id
            ),
            _update AS (
                UPDATE l10n_mx_edi_certificate c
                   SET company_id = info.company_ids[1]
                  FROM info
                 WHERE c.id = info.certificate_id
            )
            INSERT INTO l10n_mx_edi_certificate(company_id, content, key, password, serial_number, date_start, date_end, create_uid, write_uid)
                 SELECT unnest(info.company_ids[2:]), c.content, c.key, c.password, c.serial_number, c.date_start, c.date_end, c.create_uid, c.write_uid
                   FROM l10n_mx_edi_certificate AS c
                   JOIN info
                     ON info.certificate_id = c.id
                  WHERE array_length(info.company_ids, 1) > 1
        """
    )

    # drop the m2m table as we remove the m2m relationship
    cr.execute("DROP TABLE l10n_mx_edi_certificate_res_company_rel")

    # Since this field is part of a compute computing multiple fields, the column has to be created manually to prevent the
    # orm to call the compute.
    util.create_column(cr, "account_move", "l10n_mx_edi_invoice_cancellation_reason", "varchar")

    # When migrating from 16.0 to 16.4+, the table doesn't exist yet.
    if util.table_exists(cr, "l10n_mx_edi_document"):
        util.remove_field(cr, "l10n_mx_edi.document", "cancel_payment_button_needed")
        util.create_column(cr, "l10n_mx_edi_document", "attachment_origin", "varchar")
        util.create_column(cr, "l10n_mx_edi_document", "attachment_uuid", "varchar")
        util.explode_execute(
            cr,
            """
                UPDATE l10n_mx_edi_document
                SET attachment_origin = '<TO_COMPUTE>'
                WHERE l10n_mx_edi_document.attachment_id IS NOT NULL
            """,
            table="l10n_mx_edi_document",
        )
