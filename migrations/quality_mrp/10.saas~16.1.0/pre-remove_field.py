# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'quality_point', 'operation_id', 'int4')

    cr.execute("""
        WITH routing AS (
            SELECT (array_agg(id ORDER BY sequence, id))[1] as id, workcenter_id
            FROM mrp_routing_workcenter
            WHERE workcenter_id IS NOT NULL
            GROUP BY workcenter_id
        )
        UPDATE quality_point q
        SET operation_id = r.id
        FROM routing r
        WHERE q.workcenter_id = r.workcenter_id
    """)

    util.remove_field(cr, 'quality.point', 'workcenter_id')
