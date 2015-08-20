# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # currencies aren't per company anymore, but rates are.
    util.remove_record(cr, 'base.res_currency_rule')
    util.create_column(cr, 'res_currency_rate', 'company_id', 'int4')
    cr.execute("""UPDATE res_currency_rate r
                     SET company_id = c.company_id
                    FROM res_currency c
                   WHERE c.id = r.currency_id
               """)

    cr.execute("""SELECT array_agg(id) as ids
                    FROM res_currency
                   GROUP BY lower(name)
                  HAVING COUNT(id) > 1""")

    todel = []
    for row in cr.fetchall():
        ids = row[0]
        ids.sort()
        cid, other_ids = ids[0], ids[1:]
        todel.extend(other_ids)

        for oid in other_ids:
            util.replace_record_references(cr, ('res.currency', oid), ('res.currency', cid))

        cr.execute("""UPDATE res_currency
                         SET active=CASE WHEN 1 = ANY(SELECT 1
                                                    FROM res_currency
                                                   WHERE id IN %s
                                                     AND active=true)
                                         THEN true
                                         ELSE active
                                    END
                       WHERE id=%s
                   """, [tuple(other_ids), cid])

    if todel:
        cr.execute('DELETE FROM res_currency WHERE id IN %s', [tuple(todel)])
