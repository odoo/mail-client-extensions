# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # for databases born before 9.0, some cleanup should be made
    util.remove_field(cr, 'account_followup.followup', 'followup_line')
    util.import_script('account_reports_followup/9.0.1.0/pre-20-models.py').migrate(cr, version)

    cr.execute("DROP INDEX IF EXISTS ir_model_data_module_name_uniq_index")  # will be recreated later
    cr.execute("""
        DELETE FROM ir_model_data WHERE id IN (
             SELECT d.id
               FROM ir_model_data d
          LEFT JOIN ir_model_fields f ON (f.id = d.res_id)
              WHERE d.model='ir.model.fields'
                AND f.id IS NULL
        )
    """)
    cr.execute("""
        UPDATE ir_model_fields f
           SET model = m.model
          FROM ir_model m
         WHERE m.id = f.model_id
    """)
    cr.execute("""
        UPDATE ir_model_data d
           SET name = CONCAT('field_', replace(f.model, '.', '_'), '__', f.name)
          FROM ir_model_fields f
         WHERE d.model='ir.model.fields'
           AND d.res_id = f.id
           AND d.name LIKE 'field\_%'
    """)
