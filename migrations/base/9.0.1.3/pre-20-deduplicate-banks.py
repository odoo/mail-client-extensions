# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'res_partner_bank', 'sanitized_acc_number', 'varchar')
    cr.execute("""UPDATE res_partner_bank
                     SET sanitized_acc_number = upper(regexp_replace(acc_number,'\W+', '', 'g'))
               """)

    todel = []
    # XXX what if duplicated are not linked to the same partner?
    cr.execute("""SELECT array_agg(id ORDER BY coalesce(write_date, create_date) DESC)
                    FROM res_partner_bank
                GROUP BY sanitized_acc_number
                  HAVING count(id) > 1
                """)
    for ids, in cr.fetchall():
        bid, other_ids = ids[0], ids[1:]
        todel.extend(other_ids)

        for oid in other_ids:
            util.replace_record_references(cr, ('res.partner.bank', oid), ('res.partner.bank', bid))

    if todel:
        cr.execute('DELETE FROM res_partner_bank WHERE id IN %s', [tuple(todel)])
