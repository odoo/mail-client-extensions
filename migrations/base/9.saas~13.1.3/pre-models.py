# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'ir_ui_menu', 'active', 'boolean')
    cr.execute('UPDATE ir_ui_menu SET active=true')

    cr.execute("SELECT id FROM res_currency WHERE name='TJS'")
    [tjs] = cr.fetchone() or [None]
    if tjs:
        cr.execute("""
            INSERT INTO ir_model_data(module, name, model, res_id, noupdate)'
                 VALUES ('base', 'TJS', 'res.currency', %s, true)
        """, [tjs])

    util.create_column(cr, 'res_partner', 'partner_share', 'boolean')
    cr.execute("""
        WITH partshare AS (
            SELECT p.id, COALESCE(true = ANY(array_agg(u.share)), true) as share
              FROM res_partner p
         LEFT JOIN res_users u ON (p.id = u.partner_id)
          GROUP BY p.id
        )
        UPDATE res_partner p
           SET partner_share = s.share
          FROM partshare s
         WHERE s.id = p.id
    """)
