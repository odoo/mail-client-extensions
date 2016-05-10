# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    root = util.ref(cr, 'base.partner_root')
    if not root:
        cr.execute('SELECT partner_id FROM res_users WHERE id=1')
        root, = cr.fetchone()

    cr.execute('SELECT lang FROM res_partner WHERE id=%s', [root])
    root_lang, = cr.fetchone()

    # force activate admin lang
    cr.execute('UPDATE res_lang SET active=true WHERE code=%s', [root_lang])

    # reset lang of partners with an inactive lang
    cr.execute("""
        UPDATE res_partner
           SET lang = %s
         WHERE lang NOT IN (SELECT lang FROM res_lang WHERE active)
    """, [root_lang])
