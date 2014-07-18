# -*- coding: utf-8 -*-
from collections import defaultdict
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # move theses fields from product_packaging to product_ul
    for c in ['height', 'width', 'length', 'weight']:
        util.create_column(cr, 'product_ul', c, 'float8')

    # array_agg cannot aggregate arrays, do it in python
    uls = defaultdict(set)
    cr.execute("""SELECT ul,
                         coalesce(height, 0),
                         coalesce(width, 0),
                         coalesce(length, 0),
                         coalesce(weight_ul, 0)
                    FROM product_packaging""")
    for data in cr.fetchall():
        uls[data[0]].add(tuple(data[1:]))

    for ul, sizes in uls.items():
        sizes = list(sizes)
        cr.execute("""UPDATE product_ul
                         SET height=%s, width=%s, length=%s, weight=%s
                       WHERE id=%s
                   """, sizes[0] + (ul,))
        cr.execute("""UPDATE product_ul
                         SET name=CONCAT(name, ' (', width, 'x', length, 'x', height, ')')
                       WHERE id=%s
                   """, (ul,))

        for sz in sizes[1:]:
            cr.execute("""WITH newul AS (
                            INSERT INTO product_ul(type, name, height, width, length, weight)
                                (SELECT type, CONCAT(name, ' (', %(width)s, 'x', %(length)s, 'x', %(height)s, ')'),
                                        %(height)s, %(width)s, %(length)s, %(weight)s
                                   FROM product_ul
                                  WHERE id=%(ul)s)
                              RETURNING id
                          )
                          UPDATE product_packaging
                             SET ul = (SELECT id FROM newul)
                           WHERE ul = %(ul)s
                             AND coalesce(height, 0) = %(height)s
                             AND coalesce(width, 0) = %(width)s
                             AND coalesce(length, 0) = %(length)s
                             AND coalesce(weight_ul, 0) = %(weight)s
                       """,
                       {
                           'ul': ul,
                           'height': sz[0],
                           'width': sz[1],
                           'length': sz[2],
                           'weight': sz[3],
                       })

    # cleanup old fields
    for c in ['height', 'width', 'length', 'weight_ul']:
        util.remove_column(cr, 'product_packaging', c)
