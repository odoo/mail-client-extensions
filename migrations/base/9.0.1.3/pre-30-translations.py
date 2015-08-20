# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # convert 'field', 'help', 'view' into 'model'
    cr.execute("""
        UPDATE ir_translation t
           SET type='model',
               name='ir.model.fields,field_description',
               res_id=f.id
          FROM ir_model_fields f
         WHERE f.model = split_part(t.name, ',', 1)
           AND f.name = split_part(t.name, ',', 2)
           AND t.type = 'field'
    """)
    cr.execute("""
        UPDATE ir_translation t
           SET type='model',
               name='ir.model.fields,help',
               res_id=f.id
          FROM ir_model_fields f
         WHERE f.model = split_part(t.name, ',', 1)
           AND f.name = split_part(t.name, ',', 2)
           AND t.type = 'help'
    """)

    columns, t_columns = util.get_columns(cr, 'ir_translation',
                                          ('id', 'type', 'name', 'res_id'), ['t'])
    arch_column = 'arch_db' if util.column_exists(cr, 'ir_ui_view', 'arch_db') else 'arch'
    cr.execute("""INSERT INTO ir_translation(name, type, res_id, {columns})
                       SELECT 'ir.ui.view,arch_db', 'model', v.id, {t_columns}
                         FROM ir_translation t
                         JOIN ir_ui_view v ON (v.model = t.name AND strpos(v.{arch_column}, t.src) != 0)
                        WHERE v.type = 'view'
               """.format(columns=', '.join(columns), t_columns=', '.join(t_columns), arch_column=arch_column))

    # remove deprecated (and unreachable) translations
    cr.execute("""
        DELETE
          FROM ir_translation
         WHERE type IN ('rml', 'xsl',
                        'wizard_button', 'wizard_field', 'wizard_view',
                        'field', 'help', 'view')
    """)
