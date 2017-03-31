# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'pos_config', 'sequence_line_id', 'int4')

    cr.execute("""
        UPDATE pos_config c
           SET sequence_line_id = s.id
          FROM ir_sequence s
         WHERE s.code = 'pos.order.line'
           AND (s.create_date = c.create_date
             OR abs(extract(epoch from s.create_date - c.create_date)) < 1  -- created within the same second
         )
    """)
