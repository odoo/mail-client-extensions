from odoo.upgrade import util


def migrate(cr, version):
    if not util.table_exists(cr, "account_asset"):
        # `account_asset` may be auto installed, due to new `sale_subcription` deps
        # see account_asset/16.0.1.0/pre-migrate.py
        util.create_column(cr, "account_move", "depreciation_value", "numeric", default=0)
        return  # nosemrep: no-early-return

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
            UPDATE account_move move
               SET asset_id = NULL
              FROM account_asset asset
             WHERE move.asset_id IS NOT NULL
               AND move.asset_id = asset.id
               AND asset.asset_type in ('sale', 'expense')
            """,
            "CREATE INDEX IF NOT EXISTS account_account_asset_model_idx ON account_account(asset_model)",
            "CREATE INDEX IF NOT EXISTS account_asset_model_id_idx ON account_asset(model_id)",
        ],
    )

    # In the account_accountant module we add (a) new field(s) to define the method to generate deferral entries.
    # When `account_asset` is installed, we want to calculate its value based on (potentially) already existing
    # deferral entries.
    deferred_entries_method_query = """
        UPDATE res_company company
           SET {} =
               CASE WHEN EXISTS (
                             SELECT 1
                               FROM account_asset asset
                               JOIN account_move move
                                 ON move.asset_id = asset.id
                                AND move.state = 'posted'
                              WHERE asset.company_id = company.id
                                AND asset.asset_type IN %s
                                AND asset.state NOT IN ('draft', 'cancelled')
                         )
                    THEN 'on_validation'
                    ELSE 'manual'
                END
    """
    if util.column_exists(cr, "res_company", "generate_deferred_entries_method"):
        cr.execute(
            util.format_query(cr, deferred_entries_method_query, "generate_deferred_entries_method"),
            [("sale", "expense")],
        )
    elif util.column_exists(cr, "res_company", "generate_deferred_expense_entries_method") and util.column_exists(
        cr, "res_company", "generate_deferred_revenue_entries_method"
    ):
        cr.execute(
            util.format_query(cr, deferred_entries_method_query, "generate_deferred_expense_entries_method"),
            [("expense",)],
        )
        cr.execute(
            util.format_query(cr, deferred_entries_method_query, "generate_deferred_revenue_entries_method"),
            [("sale",)],
        )

    cr.execute(
        """
            SELECT id
              FROM account_asset
             WHERE asset_type in ('sale', 'expense')
        """
    )
    util.remove_records(cr, "account_asset", [cid for (cid,) in cr.fetchall()])

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
