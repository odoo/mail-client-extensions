# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_asset.assets_search_template_extra_options")
    util.remove_view(cr, "account_asset.assets_search_template")
    util.remove_view(cr, "account_asset.main_template_assets")
    util.remove_view(cr, "account_asset.main_table_header_assets")

    # Deferred management
    cr.execute(
        """
            WITH original AS (
                SELECT rel.asset_id,
                       line.move_id
                  FROM asset_move_line_rel rel
                  JOIN account_asset asset ON asset.id = rel.asset_id
                  JOIN account_move_line line ON line.id = rel.line_id
                 WHERE asset.asset_type IN ('sale', 'expense')
            ),
            deferred AS (
                SELECT asset.id AS asset_id,
                       move.id AS move_id
                  FROM account_move move
                  JOIN account_asset asset ON asset.id = move.asset_id
                 WHERE asset.asset_type IN ('sale', 'expense')
            )
            INSERT INTO account_move_deferred_rel (original_move_id, deferred_move_id)
                 SELECT original.move_id, deferred.move_id
                   FROM original
                   JOIN deferred ON original.asset_id = deferred.asset_id
            ON CONFLICT DO NOTHING
        """
    )
    util.parallel_execute(
        cr,
        [
            """
            UPDATE account_move
               SET asset_id = NULL
              FROM account_asset
             WHERE asset_id IS NOT NULL
               AND asset_id = account_asset.id
               AND asset_type in ('sale', 'expense')
            """,
            "CREATE INDEX IF NOT EXISTS account_account_asset_model_idx ON account_account(asset_model)",
            "CREATE INDEX IF NOT EXISTS account_asset_model_id_idx ON account_asset(model_id)",
        ],
    )
    cr.execute(
        """
            SELECT id
              FROM account_asset
             WHERE asset_type in ('sale', 'expense')
        """
    )
    util.remove_records(cr, "account_asset", [cid for cid, in cr.fetchall()])

    util.remove_field(cr, "account.asset", "asset_type")
    util.remove_field(cr, "account.account", "asset_type")
    util.remove_field(cr, "account.move", "asset_asset_type")
    util.remove_field(cr, "account.move", "draft_deferred_expense_exists")
    util.remove_field(cr, "account.move", "draft_deferred_revenue_exists")
    util.remove_field(cr, "account.move", "count_deferred_revenue")
    util.remove_field(cr, "account.move", "count_deferred_expense")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("account_asset.view_account_asset_model_{purchase_,}tree"))
    util.rename_xmlid(cr, *eb("account_asset.view_account_asset_{purchase_,}tree"))
    util.remove_view(cr, "account_asset.view_account_asset_model_expense_tree")
    util.remove_view(cr, "account_asset.view_account_asset_model_sale_tree")
    util.remove_view(cr, "account_asset.view_account_asset_expense_tree")
    util.remove_view(cr, "account_asset.view_account_asset_sale_tree")
    util.remove_view(cr, "account_asset.view_account_expense_model_search")
    util.remove_view(cr, "account_asset.view_account_revenue_model_search")
    util.remove_view(cr, "account_asset.view_account_asset_expense_form")
    util.remove_view(cr, "account_asset.view_account_asset_revenue_form")

    util.remove_record(cr, "account_asset.action_account_expense_model_form")
    util.remove_record(cr, "account_asset.action_account_revenue_model_form")
    util.remove_record(cr, "account_asset.action_account_expense_form")
    util.remove_record(cr, "account_asset.action_account_revenue_form")

    util.remove_menus(
        cr,
        [
            util.ref(cr, "account_asset.menu_action_account_expense_model_recognition"),
            util.ref(cr, "account_asset.menu_action_account_revenue_model_recognition"),
            util.ref(cr, "account_asset.menu_action_account_expense_recognition"),
            util.ref(cr, "account_asset.menu_action_account_revenue_recognition"),
        ],
    )
