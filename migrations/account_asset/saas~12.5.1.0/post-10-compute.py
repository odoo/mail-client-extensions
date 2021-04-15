# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
          WITH childs AS (
             SELECT sum(book_value) as amt, parent_id
               FROM account_asset
           GROUP BY parent_id
          )
        UPDATE account_asset aa
           SET book_value = COALESCE(a.value_residual, 0.0) + COALESCE(a.salvage_value, 0.0) + COALESCE(childs.amt, 0.0)
          FROM account_asset a
     LEFT JOIN childs on a.id=childs.parent_id
         WHERE aa.id=a.id
    """
    )

    # Acquisition date should be coming from the related move lines.
    cr.execute(
        """
        UPDATE account_asset aa
           SET acquisition_date = aml.acq_date
          FROM (
               SELECT asset_id, min(date) as acq_date
                 FROM account_move_line
                WHERE asset_id IS NOT NULL
                GROUP BY asset_id
          ) AS aml
         WHERE aa.id = aml.asset_id AND aa.acquisition_date IS NULL
    """
    )

    # fallback to prorata, first_depreciation, create date if there is no move line.
    # https://github.com/odoo/enterprise/blob/ef1286f6f96c998db5697806e691193b5eb1c9cf/account_asset/models/account_asset.py#L118
    cr.execute(
        """
        UPDATE account_asset
           SET acquisition_date = COALESCE(prorata_date, first_depreciation_date, create_date)
         WHERE acquisition_date IS NULL
      """
    )
