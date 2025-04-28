from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
         WITH to_upd AS (
            SELECT c.id
              FROM pos_config c
         LEFT JOIN pos_session s
                ON s.config_id = c.id
             WHERE c.settle_due_product_id IS NULL
                OR c.deposit_product_id IS NULL
          GROUP BY c.id
            HAVING bool_and(
                           s.id IS NULL
                        OR s.state NOT IN ('opened', 'closing_control')
                   )
               AND bool_and(s.rescue IS NOT True)
        )
        UPDATE pos_config c
           SET settle_due_product_id = COALESCE(settle_due_product_id, %s),
               deposit_product_id = COALESCE(deposit_product_id, %s)
          FROM to_upd
         WHERE c.id = to_upd.id
        """,
        [util.ref(cr, "pos_settle_due.product_product_settle"), util.ref(cr, "pos_settle_due.product_product_deposit")],
    )
