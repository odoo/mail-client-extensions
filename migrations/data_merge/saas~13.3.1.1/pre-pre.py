# -*- coding: utf-8 -*-
def migrate(cr, version):
    cr.execute("""
    DELETE
      FROM ir_model_fields_selection
     WHERE field_id IN (
        SELECT f.id FROM ir_model_fields f
          JOIN ir_model m ON (f.model_id = m.id)
         WHERE m.model = 'data_merge.rule'
           AND f.name = 'match_mode'
    )
    """)
