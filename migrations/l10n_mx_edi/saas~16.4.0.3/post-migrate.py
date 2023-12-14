from odoo.upgrade import util


def migrate(cr, _version):
    cfdi_format_id = util.ref(cr, "l10n_mx_edi.edi_cfdi_3_3")

    # Migrate 'account.edi.document' to 'l10n_mx_edi.document'
    query = cr.mogrify(
        """
            INSERT INTO l10n_mx_edi_document (datetime, move_id, attachment_id, state, sat_state)
            SELECT
                COALESCE(doc.write_date, att.create_date),
                doc.move_id,
                doc.attachment_id,
                CASE WHEN move.payment_id IS NOT NULL OR move.statement_line_id IS NOT NULL
                    THEN 'payment_sent'
                    ELSE 'invoice_sent'
                END AS state,
                COALESCE(move.l10n_mx_edi_cfdi_sat_state, 'not_defined') AS sat_state
            FROM account_edi_document doc
            JOIN account_move move ON move.id = doc.move_id
            JOIN ir_attachment att ON att.id = doc.attachment_id
            WHERE doc.state = 'sent' AND doc.edi_format_id = %s
        """,
        [cfdi_format_id],
    ).decode()
    util.explode_execute(cr, query, table="account_edi_document", alias="doc")

    # Fix 'l10n_mx_edi_cfdi_state' / 'l10n_mx_edi_cfdi_sat_state'.
    query = """
        UPDATE account_move
        SET
            l10n_mx_edi_cfdi_sat_state = l10n_mx_edi_document.sat_state,
            l10n_mx_edi_cfdi_attachment_id = l10n_mx_edi_document.attachment_id,
            l10n_mx_edi_cfdi_state = 'sent'
        FROM l10n_mx_edi_document
        WHERE l10n_mx_edi_document.move_id = account_move.id
    """
    util.explode_execute(cr, query, table="l10n_mx_edi_document")

    # Update 'l10n_mx_edi_invoice_document_ids_rel' for invoices.
    query = """
        INSERT INTO l10n_mx_edi_invoice_document_ids_rel (document_id, invoice_id)
        SELECT
            doc.id AS document_id,
            doc.move_id AS invoice_id
        FROM l10n_mx_edi_document doc
        WHERE doc.state = 'invoice_sent'
    """
    util.explode_execute(cr, query, table="l10n_mx_edi_document", alias="doc")

    # Update 'l10n_mx_edi_invoice_document_ids_rel' for payments.
    query = """
        INSERT INTO l10n_mx_edi_invoice_document_ids_rel (document_id, invoice_id)
        SELECT
            pay_doc.id AS document_id,
            inv_doc.move_id AS invoice_id
        FROM l10n_mx_edi_document pay_doc
        JOIN account_move_line pay_line
            ON pay_line.move_id = pay_doc.move_id
        JOIN account_partial_reconcile partial
            ON partial.credit_move_id = pay_line.id
        JOIN account_move_line inv_line
            ON inv_line.id = partial.debit_move_id
        JOIN l10n_mx_edi_document inv_doc
            ON inv_doc.move_id = inv_line.move_id
        WHERE pay_doc.state = 'payment_sent'
            AND inv_doc.state = 'invoice_sent'
            AND {parallel_filter}
        ON CONFLICT DO NOTHING
    """
    util.explode_execute(cr, query, table="l10n_mx_edi_document", alias="pay_doc")

    # Cleanup.
    cr.execute("DELETE FROM account_edi_document WHERE edi_format_id = %s", [cfdi_format_id])
    util.remove_record(cr, "l10n_mx_edi.edi_cfdi_3_3")
