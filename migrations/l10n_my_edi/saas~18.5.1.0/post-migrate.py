from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "myinvois_document", "_tmp_related_move_id", "int4")
    query = r"""
        WITH new_myinvois_document AS (
            INSERT INTO myinvois_document(
                name,
                company_id,
                currency_id,
                myinvois_issuance_date,
                myinvois_state,
                myinvois_error_document_hash,
                myinvois_retry_at,
                myinvois_exemption_reason,
                myinvois_custom_form_reference,
                myinvois_submission_uid,
                myinvois_external_uuid,
                myinvois_validation_time,
                myinvois_document_long_id,
                active,
                _tmp_related_move_id
            )
                 SELECT
                     move.name,
                     move.company_id,
                     move.currency_id,
                     move.invoice_date,
                     move.l10n_my_edi_state,
                     move.l10n_my_error_document_hash,
                     move.l10n_my_edi_retry_at,
                     move.l10n_my_edi_exemption_reason,
                     move.l10n_my_edi_custom_form_reference,
                     move.l10n_my_edi_submission_uid,
                     move.l10n_my_edi_external_uuid,
                     move.l10n_my_edi_validation_time,
                     move.l10n_my_edi_invoice_long_id,
                     TRUE,
                     move.id
                   FROM account_move move
                  WHERE move.l10n_my_edi_state IS NOT NULL
                    AND {parallel_filter}
            ON CONFLICT DO NOTHING
            RETURNING id, _tmp_related_move_id AS move_id
        ),
        new_rel AS (
            INSERT INTO myinvois_document_invoice_rel (invoice_id, document_id)
                 SELECT new_myinvois_document.move_id, new_myinvois_document.id
                   FROM new_myinvois_document
              RETURNING invoice_id, document_id
        )
        UPDATE ir_attachment att
           SET res_model = 'myinvois.document',
               res_id = rel.document_id,
               res_field = 'myinvois_file'
          FROM new_rel rel
         WHERE rel.invoice_id = att.res_id
           AND att.res_model = 'account.move'
           AND att.res_field = 'l10n_my_edi_file'
    """
    util.explode_execute(cr, query, table="account_move", alias="move")
    # 2. We then remove all fields from the invoice that moved to the new model.
    util.remove_field(cr, "account.move", "l10n_my_error_document_hash")
    util.remove_field(cr, "account.move", "l10n_my_edi_retry_at")
    util.remove_field(cr, "account.move", "l10n_my_edi_submission_uid")
    util.remove_field(cr, "account.move", "l10n_my_edi_external_uuid")
    util.remove_field(cr, "account.move", "l10n_my_edi_validation_time")
    util.remove_field(cr, "account.move", "l10n_my_edi_invoice_long_id")
    util.remove_field(cr, "account.move", "l10n_my_edi_file")
    util.remove_field(cr, "account.move", "l10n_my_edi_file_id")

    # Cleanup the temp column
    util.remove_column(cr, "myinvois_document", "_tmp_related_move_id")
