# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    mapping_table = [
        ('[67][0123478]%', util.ref(cr, 'account.account_tag_operating')),
        ('[67]5%', util.ref(cr, 'account.account_tag_financing')),
        ('[67]6%', util.ref(cr, 'account.account_tag_investing')),
    ]
    for code, tag in mapping_table:
        cr.execute("""
            INSERT INTO account_account_account_tag
                 SELECT id, %s
                   FROM account_account
                  WHERE code SIMILAR TO %s
        """, [tag, code])
