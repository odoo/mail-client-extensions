# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # Instead of a procurement on the requisition, we have a destination move on the requisition line
    util.create_column(cr, 'purchase_requisition_line', 'move_dest_id', 'int4')
    cr.execute("""UPDATE purchase_requisition_line prl 
                    SET move_dest_id = po.move_dest_id
                    FROM purchase_requisition pr, procurement_order po
                    WHERE pr.procurement_id = po.id AND prl.requisition_id = pr.id
    """)
    util.remove_field(cr, 'purchase.requisition', 'procurement_id')
