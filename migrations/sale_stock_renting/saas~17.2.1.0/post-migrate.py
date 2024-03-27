from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT 1
          FROM ir_model_data imd
          JOIN res_groups_users_rel rgur
            ON imd.res_id = rgur.gid
         WHERE imd.module = 'sale_stock_renting'
           AND imd.name = 'group_rental_stock_picking'
         FETCH FIRST ROW ONLY
        """
    )
    # Only need to update the rental rules if the 'Rental Transfers' option is enabled.
    if cr.rowcount:
        rental_route_id = util.ref(cr, "sale_stock_renting.route_rental")
        cr.execute(
            """
            WITH default_stock_loc AS (
                SELECT sr.id,
                       sw.lot_stock_id
                  FROM res_company rc
                  JOIN stock_rule sr
                    ON rc.rental_loc_id = sr.location_src_id
                  JOIN stock_warehouse sw
                    ON sr.warehouse_id = sw.id
                   AND sw.company_id = rc.id
            )
            UPDATE stock_rule sr
               SET action = 'pull',
                   procure_method = 'make_to_stock',
                   location_dest_id = dsl.lot_stock_id,
                   route_id = %s
              FROM default_stock_loc dsl
             WHERE sr.id = dsl.id
        """,
            [rental_route_id],
        )
