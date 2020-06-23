# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_account", "multiple_assets_per_line", "boolean")
    cr.execute("UPDATE account_account SET multiple_assets_per_line = false WHERE multiple_assets_per_line IS NULL")

    util.create_m2m(cr, "asset_move_line_rel", "account_asset", "account_move_line", "asset_id", "line_id")
    cr.execute(
        """
        INSERT INTO asset_move_line_rel(line_id, asset_id)
             SELECT id, asset_id
               FROM account_move_line
              WHERE asset_id IS NOT NULL
    """
    )

    util.remove_field(cr, "account.move.line", "asset_id")

    # TODO delete_unused demo data
