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
