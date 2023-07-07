# -*- coding: utf-8 -*-
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
        cr.execute(
            f"""
            UPDATE res_company company
               SET deferred_{deferred_type}_account_id = (
                    SELECT id
                      FROM account_account
                     WHERE company_id = company.id
                       AND account_type = %s
                  ORDER BY id
                     LIMIT 1
            )
            """,
            (account_type,),
        )

    if util.module_installed(cr, "account_asset"):
        # In the current module we add a new field to define the method to generate deferral entries.
        # When `account_asset` is installed, we want to calculate its value based on (potentially) already existing
        # deferral entries.
        cr.execute(
            """
            UPDATE res_company company
               SET generate_deferred_entries_method =
                   CASE WHEN EXISTS (
                                 SELECT 1
                                   FROM account_asset asset
                                   JOIN account_move move
                                     ON move.asset_id = asset.id
                                    AND move.state = 'posted'
                                  WHERE asset.company_id = company.id
                                    AND asset.asset_type IN ('sale', 'expense')
                                    AND asset.state NOT IN ('draft', 'cancelled')
                             )
                        THEN 'on_validation'
                        ELSE 'manual'
                   END
            """
        )
