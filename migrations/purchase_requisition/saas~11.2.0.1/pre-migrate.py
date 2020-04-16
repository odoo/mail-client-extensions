# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    sequence_id = util.rename_xmlid(cr, *eb('purchase_requisition.seq_purchase_{requisition,tender}'))
    if sequence_id:
        cr.execute("""UPDATE ir_sequence
                         SET code='purchase.requisition.purchase.tender'
                       WHERE id=%s
                   """, [sequence_id])

    util.create_column(cr, 'purchase_requisition', 'currency_id', 'int4')
    cr.execute("""
        UPDATE purchase_requisition r
           SET currency_id = c.currency_id
          FROM res_company c
         WHERE c.id = r.company_id
           AND r.currency_id IS NULL
    """)

    cr.execute("DELETE FROM purchase_requisition_line WHERE requisition_id IS NULL")
    # odoo/odoo@5d2c63bf49b86b5615adaa9fc3070fc5e826da15
    util.remove_field(cr, "purchase.requisition", "account_analytic_id")
