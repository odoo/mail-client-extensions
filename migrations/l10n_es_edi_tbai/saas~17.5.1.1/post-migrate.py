from odoo.upgrade import util


def migrate(cr, version):
    # Column removed at the end
    util.create_column(cr, "l10n_es_edi_tbai_document", "_upg_move_id", "int4")

    cr.execute("""
        INSERT INTO l10n_es_edi_tbai_document(
                        state,
                        is_cancel,
                        xml_attachment_id,
                        chain_index,
                        _upg_move_id,
                        name,
                        date,
                        company_id
                    )
             SELECT 'accepted',
                    FALSE,
                    ia.id,
                    CASE
                        WHEN am.move_type IN ('out_invoice', 'out_refund') THEN am.l10n_es_tbai_chain_index
                        ELSE NULL
                    END,
                    am.id,
                    am.name,
                    am.date,
                    am.company_id
               FROM ir_attachment ia
               JOIN account_move am
                 ON ia.res_id = am.id
              WHERE ia.res_model = 'account.move'
                AND ia.res_field = 'l10n_es_tbai_post_xml'
    """)
    util.explode_execute(
        cr,
        """
        UPDATE account_move am
           SET l10n_es_tbai_post_document_id = td.id
          FROM l10n_es_edi_tbai_document td
         WHERE td._upg_move_id = am.id
           AND td.is_cancel = FALSE
        """,
        table="account_move",
        alias="am",
    )

    cr.execute("""
        INSERT INTO l10n_es_edi_tbai_document(
                        state,
                        is_cancel,
                        xml_attachment_id,
                        _upg_move_id,
                        name,
                        date,
                        company_id
                    )
            SELECT  'accepted',
                    TRUE,
                    ia.id,
                    am.id,
                    am.name,
                    am.date,
                    am.company_id
               FROM ir_attachment ia
               JOIN account_move am
                 ON ia.res_id = am.id
              WHERE ia.res_model = 'account.move'
                AND ia.res_field = 'l10n_es_tbai_cancel_xml'
    """)
    util.explode_execute(
        cr,
        """
        UPDATE account_move am
           SET l10n_es_tbai_cancel_document_id = td.id
          FROM l10n_es_edi_tbai_document td
         WHERE td._upg_move_id = am.id
           AND td.is_cancel = TRUE
        """,
        table="account_move",
        alias="am",
    )

    tbai_edi_format = util.ref(cr, "l10n_es_edi_tbai.edi_es_tbai")

    cr.execute(
        """
        UPDATE l10n_es_edi_tbai_document td
           SET state = 'to_send',
               response_message = aed.error
          FROM account_edi_document aed
         WHERE td._upg_move_id = aed.move_id
           AND aed.edi_format_id = %(tbai_edi_format)s
           AND aed.blocking_level = 'warning'
           AND ((aed.state = 'to_send' AND NOT td.is_cancel) OR (aed.state = 'to_cancel' AND td.is_cancel))
    """,
        {"tbai_edi_format": tbai_edi_format},
    )

    util.explode_execute(
        cr,
        """
        UPDATE ir_attachment ia
           SET res_model = 'account.move',
               res_id = td._upg_move_id,
               res_field = NULL
          FROM l10n_es_edi_tbai_document td
         WHERE td.xml_attachment_id = ia.id
           AND td._upg_move_id IS NOT NULL
        """,
        table="ir_attachment",
        alias="ia",
    )

    cr.execute(
        "SELECT id FROM account_edi_document WHERE edi_format_id = %(tbai_edi_format)s",
        {"tbai_edi_format": tbai_edi_format},
    )
    util.remove_records(cr, "account.edi.document", [aed_id for (aed_id,) in cr.fetchall()])

    # Set edi_state = NULL for the moves not linked to an account_edi_document
    util.explode_execute(
        cr,
        """
        WITH move_edi_document(move_id, edi_document_id) AS (
               SELECT am.id,
                      min(aed.id)
                 FROM account_move am
            LEFT JOIN account_edi_document aed
                   ON am.id = aed.move_id
                WHERE {parallel_filter}
             GROUP BY am.id
        )
        UPDATE account_move am
           SET edi_state = NULL
          FROM move_edi_document med
         WHERE am.id = med.move_id
           AND med.edi_document_id IS NULL
        """,
        table="account_move",
        alias="am",
    )

    util.remove_field(cr, "account.move", "l10n_es_tbai_post_xml")
    util.remove_field(cr, "account.move", "l10n_es_tbai_cancel_xml")

    util.remove_column(cr, "l10n_es_edi_tbai_document", "_upg_move_id")
    util.remove_column(cr, "account_move", "l10n_es_tbai_chain_index")

    util.remove_record(cr, "l10n_es_edi_tbai.edi_es_tbai")
