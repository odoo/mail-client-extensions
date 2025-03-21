from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        """
        WITH m_reset_edi_state AS (
            SELECT m.id AS move_id
              FROM account_move m
              JOIN res_company c
                ON c.id = m.company_id
              JOIN res_country country
                ON c.account_fiscal_country_id = country.id
              LEFT JOIN account_edi_document d
                ON d.move_id = m.id
             WHERE country.code='IN'
               AND d.id is NULL
               AND m.edi_state IS NOT NULL
        )
        UPDATE account_move m
           SET edi_state = NULL
          FROM m_reset_edi_state
         WHERE m.id = m_reset_edi_state.move_id
        """,
        "account_move",
        alias="m",
    )
