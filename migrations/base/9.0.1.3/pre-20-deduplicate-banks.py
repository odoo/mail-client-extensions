# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "res_partner_bank", "sanitized_acc_number", "varchar")
    cr.execute(r"""UPDATE res_partner_bank
                     SET sanitized_acc_number = upper(regexp_replace(acc_number,'\W+', '', 'g'))
               """)

    todel = []
    ref_map = {}
    unduplicate_followers = util.table_exists(cr, "mail_followers")

    # XXX what if duplicated are not linked to the same partner?
    cr.execute("""SELECT array_agg(id ORDER BY coalesce(write_date, create_date) DESC)
                    FROM res_partner_bank
                GROUP BY sanitized_acc_number, company_id
                  HAVING count(id) > 1
                """)
    for (ids,) in cr.fetchall():
        bid, other_ids = ids[0], ids[1:]
        todel.extend(other_ids)

        for oid in other_ids:
            ref_map[oid] = bid

        if unduplicate_followers:
            cr.execute(
                """DELETE FROM mail_followers WHERE id IN (
                                SELECT unnest((array_agg(id ORDER BY id))[2:array_length(array_agg(id), 1)])
                                FROM mail_followers
                                WHERE res_model='res.partner.bank' and res_id in %s
                                GROUP BY partner_id
                                HAVING count(id) > 1
                            )""",
                [tuple(ids)],
            )
    if ref_map:
        util.replace_record_references_batch(cr, ref_map, "res.partner.bank")

    if todel:
        cr.execute("DELETE FROM res_partner_bank WHERE id IN %s", [tuple(todel)])
