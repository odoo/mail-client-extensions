# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'ir_model_fields', 'relation_field_id', 'int4')
    util.create_column(cr, 'ir_model_fields', 'related_field_id', 'int4')

    cr.execute("""
        UPDATE ir_model_fields f
           SET relation_field_id = r.id
          FROM ir_model_fields r
         WHERE f.state = 'manual'
           AND r.model = f.relation
           AND r.name = f.relation_field
    """)
    # NOTE: related_field_id is computed in end- script (when all modules are loaded)
