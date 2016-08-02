# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE sale_order so
           SET opportunity_id = l.id
          FROM crm_lead l
         WHERE l.ref = 'sale.order,' || so.id
           AND so.opportunity_id IS NULL
    """)
