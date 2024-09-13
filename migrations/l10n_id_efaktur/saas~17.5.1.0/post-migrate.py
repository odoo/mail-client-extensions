from odoo.upgrade import util


def migrate(cr, version):
    # for all attachment, create one document per attachment, link the invoices, then
    # update the res_id and res_model on the attachments
    # remove the l10n_id_attachment_id after finish being used

    util.explode_execute(
        cr,
        """
        INSERT INTO l10n_id_efaktur_document (attachment_id, company_id, active, name)
             SELECT am.l10n_id_attachment_id,
                    am.company_id,
                    true,
                    format(
                        '%s - Efaktur (%s)',
                        to_char(CURRENT_DATE, 'YYYYMMDD'),
                        CASE cardinality(array_agg(am.name))
                            WHEN 1 THEN min(am.name)
                            ELSE (array_agg(am.name ORDER BY am.id))[1] || '....' ||
                                 (array_agg(am.name ORDER BY am.id DESC))[1]
                        END
                    ) AS name
               FROM account_move am
               JOIN ir_attachment ia
                 ON am.l10n_id_attachment_id = ia.id
              WHERE {parallel_filter}
           GROUP BY am.l10n_id_attachment_id, am.company_id
        """,
        table="ir_attachment",
        alias="ia",
    )

    query = """
        UPDATE ir_attachment att
           SET res_model = 'l10n_id_efaktur.document',
               res_id = doc.id
          FROM l10n_id_efaktur_document doc
         WHERE doc.attachment_id = att.id
    """
    util.explode_execute(cr, query, table="ir_attachment", alias="att")

    query = """
        UPDATE account_move move
           SET l10n_id_efaktur_document = att.res_id
          FROM ir_attachment att
         WHERE att.id = move.l10n_id_attachment_id
    """
    util.explode_execute(cr, query, table="account_move", alias="move")

    util.remove_column(cr, "account_move", "l10n_id_attachment_id")
