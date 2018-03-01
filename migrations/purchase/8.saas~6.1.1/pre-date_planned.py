# -*- coding: utf-8 -*-

import util


def migrate(cr, version):
    util.drop_depending_views(cr, 'purchase_order_line', 'date_planned')
    cr.execute("""
        ALTER TABLE purchase_order_line
            ALTER COLUMN date_planned TYPE timestamp without time zone
    """)
    cr.execute("""
        WITH _tz AS (
            SELECT l.id, COALESCE(d.tz, lwp.tz, lcp.tz, owp.tz, ocp.tz, 'UTC') as tz
              FROM purchase_order_line l
              JOIN purchase_order o ON (o.id = l.order_id)
         LEFT JOIN res_partner d ON (d.id = o.dest_address_id)
         LEFT JOIN res_users lw ON (lw.id = l.write_uid)
         LEFT JOIN res_partner lwp ON (lwp.id = lw.partner_id)
         LEFT JOIN res_users lc ON (lc.id = l.create_uid)
         LEFT JOIN res_partner lcp ON (lcp.id = lc.partner_id)
         LEFT JOIN res_users ow ON (ow.id = o.write_uid)
         LEFT JOIN res_partner owp ON (owp.id = ow.partner_id)
         LEFT JOIN res_users oc ON (oc.id = o.create_uid)
         LEFT JOIN res_partner ocp ON (ocp.id = oc.partner_id)
        )
        UPDATE purchase_order_line l
           SET date_planned = (date_planned + interval '12 hours') at time zone _tz.tz at time zone 'UTC'
          FROM _tz
         WHERE _tz.id = l.id
    """)
