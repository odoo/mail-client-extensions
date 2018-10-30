# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("""
        UPDATE account_asset_asset a
           SET account_analytic_id = c.account_analytic_id
          FROM account_asset_category c
         WHERE c.id = a.category_id
           AND a.account_analytic_id IS NULL
    """)

    cr.execute("""
        INSERT INTO account_analytic_tag_account_asset_asset_rel(account_asset_asset_id, account_analytic_tag_id)
             SELECT a.id, r.account_analytic_tag_id
               FROM account_asset_asset a
               JOIN account_analytic_tag_account_asset_category_rel r ON r.account_asset_category_id = a.category_id
             EXCEPT
             SELECT account_asset_asset_id, account_analytic_tag_id
               FROM account_analytic_tag_account_asset_asset_rel
    """)
