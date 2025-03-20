from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE res_company company
           SET deferred_journal_id = (
                SELECT id
                  FROM account_journal
                 WHERE company_id = company.id
                   AND "type" = 'general'
              ORDER BY id
                 LIMIT 1
        )
         WHERE company.deferred_journal_id IS NULL
    """
    )

    for deferred_type, account_type in (["expense", "asset_current"], ["revenue", "liability_current"]):
        query = util.format_query(
            cr,
            """
            UPDATE res_company company
               SET {} = (
                    SELECT id
                      FROM account_account
                     WHERE company_id = company.id
                       AND account_type = %s
                  ORDER BY id
                     LIMIT 1
            )
            """,
            f"deferred_{deferred_type}_account_id",
        )
        cr.execute(query, [account_type])
