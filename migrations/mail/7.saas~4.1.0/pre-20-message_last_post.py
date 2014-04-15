# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""SELECT model
                    FROM ir_model_fields
                   WHERE name=%s
                     AND ttype=%s
                     AND relation=%s
               """, ('message_ids', 'one2many', 'mail.message'))

    for model, in cr.fetchall():
        table = util.table_of_model(cr, model)
        if not util.table_exists(cr, table):
            continue

        util.create_column(cr, table, 'message_last_post', 'timestamp without time zone')
        cr.execute("""UPDATE "{table}" t
                         SET message_last_post = (SELECT MAX(date)
                                                    FROM mail_message
                                                   WHERE model = %s
                                                     AND res_id = t.id)
                   """.format(table=table), (model,))
