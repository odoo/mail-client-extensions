# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'payment_acquirer', 'capture_manually', 'boolean')
    cr.execute("UPDATE payment_acquirer SET capture_manually = (auto_confirm='authorize')")

    util.create_column(cr, 'payment_token', 'verified', 'boolean')
    cr.execute("""
        WITH done_tx AS (
            SELECT k.id, array_agg(x.state) && ARRAY['done', 'refunded']::varchar[] as verified
              FROM payment_token k
         LEFT JOIN payment_transaction x ON (k.id = x.payment_token_id)
          GROUP BY k.id
        )
        UPDATE payment_token t
           SET verified = d.verified
          FROM done_tx d
         WHERE d.id = t.id
    """)
