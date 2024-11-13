# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # there is still some referencing menu to old models (models still there)
    # remove them + all referencing data
    models = ['document.ftp.browse', 'ir.ui.view_sc', 'google.docs.config', 'edi.document']
    for model in models:
        util.delete_model(cr, model)

    # 8.0 adds FK on ir_actions submodels (were missing before), so we need to
    # cleanup the frequently dangling ones: write_uid/create_uid
    for table in ('ir_act_client', 'ir_act_url', 'ir_act_window',
                  'ir_act_window_view', 'ir_act_report_xml',
                  'ir_act_server'):
        cr.execute("""
                    UPDATE "%s" SET create_uid = 1 WHERE NOT EXISTS
                        (SELECT 1 FROM res_users WHERE id = "%s".create_uid)
                   """ % (table, table))

        cr.execute("""
                    UPDATE "%s" SET write_uid = 1 WHERE NOT EXISTS
                        (SELECT 1 FROM res_users WHERE id = "%s".write_uid)
                   """ % (table, table))

    # make sure the column name is actually filled everywhere before applying
    # not null
    for table in ('ir_act_client', 'ir_act_url', 'ir_act_window',
                  'ir_act_report_xml', 'ir_act_server'):
        cr.execute("""
            UPDATE "%s" SET name = id WHERE name IS NULL OR name = '';
            ALTER TABLE "%s" ALTER COLUMN name DROP DEFAULT;
            """ % (table, table))

    # add missing PKs from 7.0
    cr.execute(
        """
        SELECT c.relname
          FROM pg_class c
     LEFT JOIN pg_constraint p
            ON p.conrelid = c.oid
           AND p.contype = 'p'
         WHERE c.relname IN ('ir_model_constraint', 'ir_model_relation')
           AND p.oid IS NULL
        """
    )
    for table_name, in cr.fetchall():
        cr.execute(util.format_query(cr, "ALTER TABLE {} ADD PRIMARY KEY (id)", table_name))
