# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        UPDATE account_analytic_line aal
           SET name = translation.value
          FROM (
                  SELECT DISTINCT res_id,
                         LAST_VALUE(value) OVER(PARTITION BY res_id
                                                ORDER BY id
                                                RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as value
                    FROM ir_translation
                   WHERE type='model' AND name='account.analytic.line,name' AND state='translated'
               ) translation
         WHERE aal.id = translation.res_id
           AND aal.name != translation.value
    """
    )
    cr.execute(
        """
        DELETE
          FROM ir_translation
         WHERE type = 'model' AND name LIKE 'account.analytic.line,name'
     """
    )
