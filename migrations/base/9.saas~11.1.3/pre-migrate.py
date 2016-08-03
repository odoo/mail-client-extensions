# -*- coding: utf-8 -*-
import logging
import os

from openerp.addons.base.ir.ir_cron import str2tuple
from openerp.addons.base.maintenance.migrations import util

NS = 'openerp.addons.base.maintenance.migrations.base.saas~11.'
_logger = logging.getLogger(NS + __name__)

def migrate(cr, version):
    cr.execute("DROP TABLE ir_autovacuum")   # should always have been a abstract model

    # adapt crons running server actions
    # function should be @api.model
    cr.execute("""
        UPDATE ir_cron
           SET function='_run_actions'
         WHERE model='ir.actions.server'
           AND function='run'
    """)

    if os.environ.get('ODOO_MIG_S12_CRONS_VALID'):
        return

    cr.execute("""
        SELECT id, model, function, args
          FROM ir_cron
         WHERE model != 'ir.actions.server'
    """)
    matches = False
    for cid, model, func, args in cr.fetchall():
        args_eval = str2tuple(args)
        if (args_eval and
            (type(args_eval[0]) in (int, long) or          # ignore booleans
             (isinstance(args_eval[0], (list, tuple)) and
              all(type(x) in (int, long) for x in args_eval[0]))
             )):
            matches = True
            _logger.error('Cron #%s calls env[%r].%s(*%s). Using `id` or `ids` as first argument '
                          'may not works if method is `@api.multi`.',
                          cid, model, func, args)

    if matches:
        raise util.MigrationError('Suspicious crons found')
