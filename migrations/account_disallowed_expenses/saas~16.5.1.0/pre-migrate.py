# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_constraint(
        cr, "account_disallowed_expenses_category", "account_disallowed_expenses_category_unique_code_in_country"
    )
    cr.execute(
        """
          WITH duplicates AS (
              SELECT code,
                     ARRAY_AGG(id ORDER BY id) AS ids
                FROM account_disallowed_expenses_category
               GROUP BY code
              HAVING COUNT(*) > 1
          )
        UPDATE account_disallowed_expenses_category category
           SET code = duplicates.code || '(' || ARRAY_POSITION(duplicates.ids, category.id) || ')'
          FROM duplicates
         WHERE category.id = ANY(duplicates.ids)
        """
    )
