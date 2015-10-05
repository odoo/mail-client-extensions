# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_m2m(cr, 'purchase_requisition_supplier_rel',
                    'purchase_requisition_partner', 'res_partner', 'requisition_id', 'partner_id')
    cr.execute("""INSERT INTO purchase_requisition_supplier_rel(requisition_id, partner_id)
                       SELECT id, partner_id
                         FROM purchase_requisition_partner
               """)
