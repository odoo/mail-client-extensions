# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    sequence_id = util.ref(cr, 'purchase_requisition.seq_purchase_tender')
    if sequence_id:
        cr.execute("""UPDATE ir_sequence
                         SET company_id=NULL
                       WHERE id=%s
                   """, [sequence_id])

