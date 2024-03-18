from odoo.upgrade import util


def migrate(cr, version):
    """
    Computes the newly added field asset_move_type for existing records.
    This field describe the relation a move can have towards an asset,
    for example a depreciation, purchase, sale, ...

    Two update queries are executed:
    - The first one is based on the field asset_id on the account.move model, and
        is used for depreciations, negative revaluations, disposals and sales.
    - The other one is based on the field asset_ids on the account.move model, and
        is used for purchases and positive revaluations

    Each update query concern a set of data that is exclusive, as a move can either
    have asset_id or asset_ids defined, not both.
    """
    util.create_column(cr, "account_move", "asset_move_type", "varchar")
    util.explode_execute(
        cr,
        """
        WITH LineCounts AS (
            SELECT am.id as move_id,
                   COUNT(aml.id) AS line_count,
                   am.asset_value_change,
                   asset.state
              FROM account_move am
              JOIN account_move_line aml
                ON aml.move_id = am.id
              JOIN account_asset asset
                ON asset.id = am.asset_id
             WHERE {parallel_filter}
          GROUP BY am.id, asset.id
        )
        UPDATE account_move am
           SET asset_move_type = CASE
                   WHEN line_counts.asset_value_change IS TRUE THEN 'negative_revaluation'
                   WHEN line_counts.state != 'close' OR line_counts.line_count <= 2 THEN 'depreciation'
                   WHEN line_counts.line_count = 3 THEN 'disposal'
                   ELSE 'sale'
               END
          FROM LineCounts line_counts
         WHERE am.id = line_counts.move_id
        """,
        table="account_move",
        alias="am",
    )

    # Focus on the purchase and positive revaluation
    # Cannot affect the same data of the above query as move can not have asset_id
    # and asset_ids defined at the same time
    # Set the value to purchase if a move is both a purchase and a positive revaluation
    util.explode_execute(
        cr,
        """
        WITH AssetMoveTypeValues AS (
            SELECT aml.move_id,
                   CASE
                       WHEN COUNT(asset.parent_id) < COUNT(*) THEN 'purchase'
                       ELSE 'positive_revaluation'
                   END AS asset_move_type
              FROM account_move_line aml
              JOIN asset_move_line_rel rel
                ON rel.line_id = aml.id
              JOIN account_move am
                ON am.id = aml.move_id
              JOIN account_asset asset
                ON asset.id = rel.asset_id
             WHERE {parallel_filter}
               AND am.asset_move_type IS NULL
          GROUP BY aml.move_id
        )
        UPDATE account_move am
           SET asset_move_type = amtv.asset_move_type
          FROM AssetMoveTypeValues amtv
         WHERE am.id = amtv.move_id
        """,
        table="account_move",
        alias="am",
    )

    # Computes the newly added field net_gain_on_sale for existing records
    # This field is set on the asset and defines the net value obtained when
    # either selling or disposing an asset.
    util.create_column(cr, "account_asset", "net_gain_on_sale", "numeric")
    util.explode_execute(
        cr,
        """
        WITH LatestSaleBalance AS (
            SELECT am.asset_id,
                   MAX(aml.id) AS line_id
              FROM account_move am
              JOIN account_move_line aml
                ON aml.move_id = am.id
              JOIN account_asset asset
                ON asset.id = am.asset_id
             WHERE {parallel_filter}
               AND am.asset_move_type IN ('sale', 'disposal')
          GROUP BY am.asset_id
        )
        UPDATE account_asset asset
           SET net_gain_on_sale = -aml.balance
          FROM LatestSaleBalance lsb
          JOIN account_move_line aml
            ON aml.id = lsb.line_id
         WHERE lsb.asset_id = asset.id
        """,
        table="account_asset",
        alias="asset",
    )
