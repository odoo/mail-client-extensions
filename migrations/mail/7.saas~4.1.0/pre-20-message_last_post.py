# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""SELECT model
                    FROM ir_model_fields f
                   WHERE name=%s
                     AND ttype=%s
                     AND relation=%s
                     AND EXISTS(SELECT 1 FROM mail_message WHERE model = f.model)
               """, ('message_ids', 'one2many', 'mail.message'))

    for model, in cr.fetchall():
        table = util.table_of_model(cr, model)
        if not util.table_exists(cr, table):
            continue

        util.create_column(cr, table, 'message_last_post', 'timestamp without time zone')
        cr.execute("""
            WITH sel AS (
                SELECT res_id as id, MAX(date) AS last_post
                  FROM mail_message
                 WHERE model = %s
                 GROUP BY res_id)
            UPDATE {table} t
                SET message_last_post = sel.last_post
                FROM sel
                WHERE t.id = sel.id
        """.format(table=table), (model,))
