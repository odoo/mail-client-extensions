from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_bank_statement", "extract_state", "varchar", default="no_extract_requested")
    util.create_column(cr, "account_bank_statement", "extract_state_processed", "bool", default=False)
    util.create_column(cr, "account_bank_statement", "is_in_extractable_state", "bool", default=False)

    query = """
        WITH _no_line AS (
            SELECT s.id
              FROM account_bank_statement s
         LEFT JOIN account_bank_statement_line l
                ON l.statement_id = s.id
             WHERE l.id IS NULL
               AND {parallel_filter}
        )
        UPDATE account_bank_statement s
           SET is_in_extractable_state = true
          FROM _no_line n
         WHERE n.id = s.id
    """
    util.explode_execute(cr, query, table="account_bank_statement", alias="s")
