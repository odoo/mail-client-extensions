# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("""
          WITH childs AS (
             SELECT sum(book_value) as amt, parent_id
               FROM account_asset
           GROUP BY parent_id
          )
        UPDATE account_asset aa
           SET book_value=a.value_residual+a.salvage_value+COALESCE(childs.amt, 0.0)
          FROM account_asset a
     LEFT JOIN childs on a.id=childs.parent_id
         WHERE aa.id=a.id
    """)

    # Acquisition date should be coming from the related move lines.
    # TODO(jde): fallback on asset's create_date if there is no move line.
    cr.execute("""
        UPDATE account_asset aa
           SET acquisition_date = aml.acq_date
          FROM (
               SELECT asset_id, min(date) as acq_date
                 FROM account_move_line
                WHERE asset_id IS NOT NULL
                GROUP BY asset_id
          ) AS aml
         WHERE aa.id = aml.asset_id AND aa.acquisition_date IS NULL
    """)
