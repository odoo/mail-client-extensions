from odoo.upgrade import util


def migrate(cr, version):
    if util.column_exists(cr, "account_move", "l10n_id_qris_invoice_details"):
        # field introduced in saas~17.3
        query = """
            INSERT INTO l10n_id_qris_transaction(
                model, model_id,
                qris_invoice_id, qris_amount, qris_content,
                qris_creation_datetime
            )
            SELECT 'account.move', m.id,
                    j.qris_invoice_id, j.qris_amount, j.qris_content,
                    j.qris_creation_datetime at time zone 'Asia/Jakarta' at time zone 'UTC'
              FROM account_move m,
                   jsonb_to_recordset(m.l10n_id_qris_invoice_details)
                   AS j(qris_invoice_id varchar, qris_amount int, qris_content varchar, qris_creation_datetime timestamp)
             WHERE m.l10n_id_qris_invoice_details IS NOT NULL
               AND {parallel_filter}
        """
        util.explode_execute(cr, query, table="account_move", alias="m")

    util.remove_field(cr, "account.move", "l10n_id_qris_invoice_details")
