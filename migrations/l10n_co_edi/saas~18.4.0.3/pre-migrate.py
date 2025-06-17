from odoo.upgrade import util


def migrate(cr, version):
    # Sql version of `_compute_operation_type` in l10n_co_edi/models/account_invoice.py
    util.create_column(cr, "account_move", "l10n_co_edi_operation_type", "varchar")
    query = """
        WITH _co_moves AS (
            SELECT move.id, move.move_type, move.reversed_entry_id, move.debit_origin_id, journal.l10n_co_edi_debit_note
              FROM account_move move
              JOIN account_journal journal
                ON journal.id = move.journal_id
              JOIN res_company company
                ON company.id = move.company_id
              JOIN res_country country
                ON country.id = company.account_fiscal_country_id
             WHERE {parallel_filter}
               AND country.code = 'CO'
        )
        UPDATE account_move am
           SET l10n_co_edi_operation_type = CASE
               WHEN move.move_type = 'out_refund' AND move.reversed_entry_id IS NOT NULL THEN '20'
               WHEN move.move_type = 'out_refund' AND move.reversed_entry_id IS NULL THEN '22'
               WHEN move.l10n_co_edi_debit_note AND move.debit_origin_id IS NOT NULL THEN '30'
               WHEN move.l10n_co_edi_debit_note AND move.debit_origin_id IS NULL THEN '32'
               ELSE '10' END
          FROM _co_moves move
         WHERE move.id = am.id
    """
    util.explode_execute(cr, query, table="account_move", alias="move")
