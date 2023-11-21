from odoo.upgrade import util


def migrate(cr, version):
    # Removing the asset removes also the move, to be safe we need to ensure the move is in draft
    cr.execute(
        """
        WITH info AS (
            SELECT a.id AS asset_id,
                   a.name AS asset_name,
                   array_agg(depreciation_entry.id ORDER BY depreciation_entry.id) AS move_ids,
                   array_agg(
                       CONCAT(depreciation_entry.name, ' (state=', COALESCE(depreciation_entry.state, 'draft'), ')')
                       ORDER BY depreciation_entry.id
                   ) AS move_names,
                   bool_or(COALESCE(depreciation_entry.state, 'draft') != 'draft') AS wrong
              FROM account_asset a
              JOIN asset_move_line_rel rel
                ON a.id = rel.asset_id
              JOIN account_move_line line
                ON line.id = rel.line_id
              JOIN account_move vendor_bill
                ON vendor_bill.id = line.move_id
         LEFT JOIN account_move depreciation_entry
                ON depreciation_entry.asset_id = a.id
             WHERE a.state = 'draft'
               AND vendor_bill.state = 'draft'
             GROUP BY a.id, a.name
        ), _removed AS (
            DELETE FROM account_asset a
                  USING info
                  WHERE info.asset_id = a.id
                    AND NOT info.wrong
        ) SELECT * FROM info WHERE wrong
        """
    )
    wrong_data = cr.fetchall()
    if not wrong_data:
        return
    msg = """
    <details>
    <summary>
        Some draft Assets linked to draft Vendor Bills were also linked to a *non-draft* Depreciation Move.
        This is an invalid configuration. Please check the assets and moves listed below.
    </summary>
    <ul>
        {}
    </ul>
    </details>
    """.format(
        "\n        ".join(
            "<li>The asset {} is linked to the depreciation move(s) {}</li>".format(
                util.get_anchor_link_to_record("account.asset", asset_id, asset_name),
                ", ".join(
                    util.get_anchor_link_to_record("account.move", move_id, move_name)
                    for move_id, move_name in zip(move_ids, move_names)
                ),
            )
            for asset_id, asset_name, move_ids, move_names, _ in wrong_data
        )
    )
    util.add_to_migration_reports(category="Accounting", format="html", message=msg)
