# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    util.create_column(cr, 'sale_order', 'invoice_shipping_on_delivery', 'boolean')
    cr.execute("""UPDATE sale_order o
                     SET invoice_shipping_on_delivery = NOT EXISTS(
                            SELECT 1 FROM sale_order_line WHERE order_id=o.id AND is_delivery)
               """)

    util.rename_field(cr, 'delivery.carrier', 'normal_price', 'fixed_price')
    util.create_column(cr, 'delivery_carrier', 'delivery_type', 'varchar')    # for db < saas-6
    util.create_column(cr, 'delivery_carrier', 'state', 'varchar')
    util.create_column(cr, 'delivery_carrier', 'zip_from', 'varchar')
    util.create_column(cr, 'delivery_carrier', 'zip_to', 'varchar')
    cr.execute("""
        UPDATE delivery_carrier
           SET delivery_type=CASE WHEN coalesce(fixed_price, 0) = 0 THEN 'base_on_rule'
                                  ELSE 'fixed'
                              END
         WHERE coalesce(delivery_type, 'grid') = 'grid'
    """)
    cr.execute("UPDATE delivery_carrier SET state='production'")

    # TODO duplicate carrier per grid + copy country_ids + state_ids + zip_from + zip_to on carrier

    # merge grids (of the same carrier) with the sames lines & zip_{from,to}
    todel = []
    cr.execute("""
        SELECT array_agg(g.id)
          FROM (SELECT g.id, array_agg(ROW(l.price_type, l.list_price, l.variable_factor,
                                           l.operator, l.max_value, l.standard_price)
                                       ORDER BY l.sequence) lines
                  FROM delivery_grid g
            RIGHT JOIN delivery_grid_line l ON (l.grid_id = g.id)
              GROUP BY g.id
                ) a
          JOIN delivery_grid g ON (g.id=a.id)
      GROUP BY g.carrier_id, a.lines, g.zip_from, g.zip_to
        HAVING count(g.id) > 1
    """)
    for grid_ids, in cr.fetchall():
        gid, other_ids = grid_ids[0], grid_ids[1:]
        todel.extend(other_ids)
        # merge countries & states
        cr.execute("""UPDATE delivery_grid_country_rel r
                         SET grid_id=%s
                       WHERE grid_id=ANY(%s)
                         AND NOT EXISTS(SELECT 1
                                          FROM delivery_grid_country_rel r2
                                         WHERE r2.grid_id=%s
                                           AND r2.country_id=r.country_id
                                        )
                   """, [gid, other_ids, gid])
        cr.execute("""UPDATE delivery_grid_state_rel r
                         SET grid_id=%s
                       WHERE grid_id=ANY(%s)
                         AND NOT EXISTS(SELECT 1
                                          FROM delivery_grid_state_rel r2
                                         WHERE r2.grid_id=%s
                                           AND r2.state_id=r.state_id
                                        )
                   """, [gid, other_ids, gid])

    if todel:
        # wil delete cascade line & country+state m2m entries
        cr.execute("DELETE FROM delivery_grid WHERE id=ANY(%s)", [todel])

    columns, c_columns = map(','.join, util.get_columns(cr, 'delivery_carrier',
                                                        ('id', 'zip_from', 'zip_to'), ['c']))

    util.create_column(cr, 'delivery_carrier', '_tmp', 'int4')
    cr.execute("""SELECT carrier_id, array_agg(id)
                    FROM delivery_grid
                GROUP BY carrier_id     -- only by carrier_id
               """)
    for cid, grids in cr.fetchall():
        cr.execute("""UPDATE delivery_carrier c
                         SET zip_from=g.zip_from,
                             zip_to=g.zip_to
                        FROM delivery_grid g
                       WHERE c.id=%s
                         AND g.id=%s
                   """, [cid, grids[0]])
        grids.pop(0)
        if grids:
            # duplicate carrier (1 per grid)
            cr.execute("""
                INSERT INTO delivery_carrier({columns}, zip_from, zip_to, _tmp)
                SELECT {c_columns}, g.zip_from, g.zip_to, g.id
                  FROM delivery_carrier c, delivery_grid g
                 WHERE c.id=%s
                   AND g.id=ANY(%s)
                   RETURNING id, _tmp
            """.format(columns=columns, c_columns=c_columns), [cid, grids])
            for ncid, gid in cr.fetchall():
                cr.execute("UPDATE delivery_grid SET carrier_id=%s WHERE id=%s", [ncid, gid])

    util.remove_column(cr, 'delivery_carrier', '_tmp')

    # line -> rule
    util.rename_model(cr, 'delivery.grid.line', 'delivery.price.rule')
    util.rename_field(cr, 'delivery.price.rule', 'type', 'variable')
    util.create_column(cr, 'delivery_price_rule', 'carrier_id', 'int4')
    cr.execute("""UPDATE delivery_price_rule r
                     SET carrier_id=g.carrier_id
                    FROM delivery_grid g
                   WHERE g.id = r.grid_id
               """)

    util.delete_model(cr, 'delivery.grid')
    util.remove_field(cr, 'delivery.price.rule', 'grid_id')

    util.rename_field(cr, 'res.partner',
                      'property_delivery_carrier', 'property_delivery_carrier_id')
