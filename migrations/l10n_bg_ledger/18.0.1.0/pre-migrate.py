from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_journal", "l10n_bg_customer_invoice", "varchar", default="01")
    util.create_column(cr, "account_journal", "l10n_bg_credit_notes", "varchar", default="03")
    util.create_column(cr, "account_journal", "l10n_bg_debit_notes", "varchar", default="02")
    util.create_column(cr, "account_move", "l10n_bg_document_type", "varchar")
    if util.column_exists(cr, "account_move", "debit_origin_id"):  # only when account_debit_note is installed
        query = """
            UPDATE account_move m
               SET l10n_bg_document_type = j.l10n_bg_debit_notes
              FROM account_journal j
             WHERE m.journal_id = j.id
               AND m.debit_origin_id IS NOT NULL
        """
        util.explode_execute(cr, query, table="account_move", alias="m")
    query = """
        UPDATE account_move m
           SET l10n_bg_document_type = CASE m.move_type
                                           WHEN 'out_invoice' THEN j.l10n_bg_customer_invoice
                                           WHEN 'in_invoice' THEN j.l10n_bg_customer_invoice
                                           ELSE j.l10n_bg_credit_notes
                                       END
          FROM account_journal j
         WHERE m.l10n_bg_document_type IS NULL
           AND m.journal_id = j.id
           AND m.move_type IN ('out_invoice', 'in_invoice', 'in_refund', 'out_refund')
    """
    util.explode_execute(cr, query, table="account_move", alias="m")
