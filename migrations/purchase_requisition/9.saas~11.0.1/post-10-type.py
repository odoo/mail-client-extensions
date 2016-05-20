# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    ex = None
    cr.execute("SELECT count(*) FROM purchase_requisition WHERE exclusive='exclusive'")
    if cr.fetchone()[0]:
        PRT = util.env(cr)['purchase.requisition.type']
        ex = PRT.create({'exclusive': 'exclusive', 'name': 'Exclusive'}).id

    mul = util.ref(cr, 'purchase_requisition.type_multi')

    cr.execute("""
        UPDATE purchase_requisition
           SET type_id = CASE WHEN exclusive='exclusive' THEN %s ELSE %s END
    """, [ex, mul])

    cr.execute("ALTER TABLE purchase_requisition ALTER COLUMN type_id SET NOT NULL")
