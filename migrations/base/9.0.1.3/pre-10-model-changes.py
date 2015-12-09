# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'ir_model', 'transient', 'boolean')

    for f in 'help related relation_table column1 column2'.split():
        util.create_column(cr, 'ir_model_fields', f, 'varchar')
    for f in 'index copy'.split():
        util.create_column(cr, 'ir_model_fields', f, 'boolean')
    util.create_column(cr, 'ir_model_fields', 'compute', 'text')

    cr.execute("UPDATE ir_model_fields SET index = (select_level != '0')")
    cr.execute("ALTER TABLE ir_model_fields DROP COLUMN select_level")
    util.rename_field(cr, 'ir.model.fields', 'select_level', 'index')

    util.move_field_to_module(cr, 'res.group', 'share', 'share', 'base')
    util.move_field_to_module(cr, 'res.users', 'share', 'share', 'base')

    util.create_column(cr, 'ir_ui_menu', 'action', 'varchar')

    cr.execute("""WITH tree_but_open AS (
                       DELETE FROM ir_values
                             WHERE model='ir.ui.menu'
                               AND key='action'
                               AND key2='tree_but_open'
                         RETURNING res_id, value
                  )
                  UPDATE ir_ui_menu m
                     SET action=t.value
                    FROM tree_but_open t
                   WHERE m.id = t.res_id
               """)

    util.rename_model(cr, 'osv_memory.autovacuum', 'ir.autovacuum')

    cr.execute("""
        CREATE TABLE res_users_log(
            id SERIAL PRIMARY KEY,
            create_uid integer,
            create_date timestamp without time zone,
            write_uid integer,
            write_date timestamp without time zone
        )
    """)
    cr.execute("""
        INSERT INTO res_users_log(create_uid, create_date)
             SELECT id, login_date
               FROM res_users
              WHERE login_date IS NOT NULL
    """)
    util.remove_column(cr, 'res_users', 'login_date')       # field still exists (now a related)

    util.create_column(cr, 'ir_attachment', 'public', 'boolean')
    cr.execute("""
        UPDATE ir_attachment
           SET public = true
         WHERE res_model = 'ir.ui.view'
           AND coalesce(res_id, 0) = 0
    """)

    # ir.model.data index cleanup
    cr.execute("""
      DROP INDEX IF EXISTS ir_model_data_module_name_index;
      DROP INDEX IF EXISTS ir_model_data_model_res_id_index;
      DROP INDEX IF EXISTS ir_model_data_module_index;
      DROP INDEX IF EXISTS ir_model_data_res_id_index;
      DROP INDEX IF EXISTS ir_model_data_model_index;
      DROP INDEX IF EXISTS ir_model_data_name_index;
      ALTER TABLE ir_model_data DROP CONSTRAINT IF EXISTS ir_model_data_module_name_uniq;
      CREATE UNIQUE INDEX ir_model_data_module_name_index ON ir_model_data (module, name);
      CREATE INDEX ir_model_data_model_res_id_index ON ir_model_data (model, res_id);
    """)
