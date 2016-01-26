# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    mapping_table = [
        ('[67][0123478]%', util.ref(cr, 'account.account_tag_operating')),
        ('[67]5%', util.ref(cr, 'account.account_tag_financing')),
        ('[67]6%', util.ref(cr, 'account.account_tag_investing')),
    ]
    for entry in mapping_table:
        cr.execute("""SELECT id from account_account WHERE code LIKE %s""", (entry[0],))
        res = cr.dictfetchall()
        if res:
            for account in res:
                cr.execute("""INSERT INTO account_account_account_tag
                    VALUES (%s, %s)
                    """, (account['id'], entry[1]))
