from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT digits FROM decimal_precision WHERE name='Product Unit'")
    res = cr.fetchone()
    precision = res[0] if res else 2

    cr.execute(
        """
        WITH mps_min AS (
            SELECT m.bom_id,
                   MIN(m.batch_size) AS min_batch_size,
                   pt.uom_id AS product_uom_id
              FROM mrp_production_schedule m
              JOIN product_product p
                ON p.id = m.product_id
              JOIN product_template pt
                ON pt.id = p.product_tmpl_id
             WHERE m.enable_batch_size
               AND m.batch_size > 0
               AND m.bom_id IS NOT NULL
          GROUP BY m.bom_id, pt.uom_id
        )
        UPDATE mrp_bom b
           SET batch_size = ROUND((m.min_batch_size * (pu.factor / bu.factor))::numeric, %s),
               enable_batch_size = TRUE
          FROM mps_min m
          JOIN uom_uom pu
            ON pu.id = m.product_uom_id
          JOIN mrp_bom br
            ON br.id = m.bom_id
          JOIN uom_uom bu
            ON bu.id = br.product_uom_id
         WHERE b.id = m.bom_id
    """,
        [precision],
    )

    util.remove_field(cr, "mrp.production.schedule", "batch_size")
    util.remove_field(cr, "mrp.production.schedule", "enable_batch_size")
