from odoo.upgrade import util


def migrate(cr, version):
    # move all l10n_id_efaktur.document data to l10n_id_efaktur_coretax.document
    # then remove the l10n_id_efaktur.document model
    cr.execute(
        """
        WITH inserted AS (
            INSERT INTO l10n_id_efaktur_coretax_document (
                            attachment_id, company_id, active, name
                        )
                 SELECT attachment_id, company_id, active, name
                   FROM l10n_id_efaktur_document
               ORDER BY id
              RETURNING id
        ), mapping AS (
            SELECT UNNEST((SELECT array_agg(i.id ORDER BY i.id) FROM inserted i)) new_id,
                   UNNEST(array_agg(o.id ORDER BY o.id)) orig_id
              FROM l10n_id_efaktur_document o
        ), updated AS (
            UPDATE account_move
               SET l10n_id_coretax_document = m.new_id
              FROM mapping m
             WHERE l10n_id_efaktur_document = m.orig_id
         RETURNING l10n_id_efaktur_document -- dummy return to ensure the update happens
        ) SELECT m.orig_id,
                 m.new_id
            FROM mapping m
        """,
    )
    mapping = dict(cr.fetchall())
    if mapping:
        util.replace_record_references_batch(
            cr, mapping, model_src="l10n_id_efaktur.document", model_dst="l10n_id_efaktur_coretax.document"
        )
    util.merge_model(cr, "l10n_id_efaktur.document", "l10n_id_efaktur_coretax.document")
    util.remove_field(cr, "account.move", "l10n_id_efaktur_document")
