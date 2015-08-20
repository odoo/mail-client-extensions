# -*- coding: utf-8 -*-
import logging
from openerp.addons.base.maintenance.migrations import util

NS = 'openerp.addons.base.maintenance.migrations.mail.9.'
_logger = logging.getLogger(NS + __name__)

def clean(cr, table, model_col='res_model', id_col='res_id'):
    cr.execute("SELECT {model_col} FROM {table} WHERE {model_col} IS NOT NULL GROUP BY {model_col}"
               .format(**locals()))
    for model, in cr.fetchall():
        adj = ''
        target_table = util.table_of_model(cr, model)
        if util.table_exists(cr, target_table):
            cr.execute("""
                WITH not_there AS (
                    SELECT t.id
                      FROM {table} t
                 LEFT JOIN {target_table} g ON (g.id=t.{id_col})
                     WHERE t.{model_col}=%s
                       AND g.id IS NULL
                )
                DELETE FROM {table} t USING not_there n WHERE t.id = n.id
            """.format(**locals()), [model])
        else:
            adj = ' unexisting'
            cr.execute("DELETE FROM {table} WHERE {model_col}=%s".format(**locals()), [model])

        deleted = cr.rowcount
        if deleted:
            _logger.debug('DELETE %(deleted)d %(table)s invalid rows for%(adj)s model %(model)s',
                          locals())


def migrate(cr, version):
    clean(cr, 'mail_followers')

    # Create missing index.
    # Without it, deletion is way loooonger!
    if not util.get_index_on(cr, 'mail_mail', 'mail_message_id'):
        cr.execute("CREATE INDEX mail_mail_mail_message_id_index ON mail_mail(mail_message_id)")

    clean(cr, 'mail_message', 'model')
