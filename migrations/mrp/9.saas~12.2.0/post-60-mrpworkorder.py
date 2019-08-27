# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("""
        WITH to_upd AS ( 
            SELECT mw.id,mrw.id as operation_id,mwc.capacity
              FROM mrp_workorder mw
               JOIN mrp_production mp ON (mp.id=mw.production_id)
               JOIN mrp_bom mb ON (mb.id= mp.bom_id)
               JOIN mrp_routing_workcenter mrw ON (mb.routing_id= mrw.routing_id)
               JOIN mrp_workcenter mwc ON (mwc.id=mrw.workcenter_id)
             WHERE mw.workcenter_id=mrw.workcenter_id
                 AND SPLIT_PART(mw.name,' - ',1) = mrw.name
          GROUP BY mw.id,mrw.id,mwc.capacity
        )
        UPDATE mrp_workorder w
           SET operation_id = u.operation_id,
               capacity = u.capacity
          FROM to_upd u
        WHERE w.id = u.id
    """)

