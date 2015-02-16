# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""CREATE TABLE purchase_requisition_supplier_rel(
                    requisition_id int4, partner_id int4)""")
    cr.execute("""INSERT INTO purchase_requisition_supplier_rel(requisition_id, partner_id)
                       SELECT id, partner_id
                         FROM purchase_requisition_partner
               """)
