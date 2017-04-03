# -*- coding: utf-8 -*-

def migrate(cr, version):
    # see https://www.postgresql.org/docs/9.3/static/datatype-numeric.html#DATATYPE-NUMERIC-TABLE
    MAXINT4 = 2147483647

    cr.execute("""
        INSERT INTO stock_location_route(name, active, sequence,
                                         product_selectable, product_categ_selectable,
                                         warehouse_selectable)
             VALUES ('Global', true, %s, false, false, false)
          RETURNING id
    """, [MAXINT4])
    [route_id] = cr.fetchone()
    cr.execute("UPDATE procurement_rule SET route_id=%s, route_sequence=%s WHERE route_id IS NULL",
               [route_id, MAXINT4])
    cr.execute("UPDATE stock_location_path SET route_id=%s, route_sequence=%s WHERE route_id IS NULL",
               [route_id, MAXINT4])
