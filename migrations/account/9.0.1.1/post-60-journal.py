# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("""SELECT j.id AS journal_id, i.id AS payment_method_id, i.payment_type 
                    FROM account_journal j, account_payment_method i 
                    WHERE j.type IN ('bank', 'cash') AND i.payment_type IN ('inbound', 'outbound')
                """)

    for record in cr.dictfetchall():
        if record['payment_type'] == 'inbound':
            cr.execute("""INSERT into account_journal_inbound_payment_method_rel(journal_id, inbound_payment_method)
                            VALUES (%s, %s)
                        """, (record['journal_id'], record['payment_method_id']))
            cr.execute("""UPDATE account_journal
                            SET at_least_one_inbound = %s
                            WHERE id = %s""", (True, record['journal_id']))
        else:
            cr.execute("""INSERT into account_journal_outbound_payment_method_rel(journal_id, outbound_payment_method)
                            VALUES (%s, %s)
                        """, (record['journal_id'], record['payment_method_id']))
            cr.execute("""UPDATE account_journal
                            SET at_least_one_outbound = %s
                            WHERE id = %s""", (True, record['journal_id']))