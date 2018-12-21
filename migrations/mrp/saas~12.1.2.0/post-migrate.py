# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("""
        UPDATE mrp_production
           SET reservation_state='confirmed'
         WHERE reservation_state='waiting'
    """)
    cr.execute("""
        SELECT id
          FROM mrp_production
         WHERE state='progress'
    """)
    prod_ids = [r[0] for r in cr.fetchall()]
    util.recompute_fields(cr, "mrp.production", ["state"], ids=prod_ids)

    cr.execute("""
        UPDATE mrp_production
           SET reservation_state=NULL
         WHERE reservation_state='none'
            OR state in ('done', 'cancel')
    """)

    cr.execute("""
        SELECT id
          FROM mrp_production
         WHERE reservation_state='partially_available'
    """)
    prod_ids = [r[0] for r in cr.fetchall()]
    util.recompute_fields(cr, "mrp.production", ["reservation_state"], ids=prod_ids)

    cr.execute("""
        UPDATE mrp_workorder w
           SET production_availability = p.reservation_state
          FROM mrp_production p
         WHERE w.production_id=p.id
    """)
