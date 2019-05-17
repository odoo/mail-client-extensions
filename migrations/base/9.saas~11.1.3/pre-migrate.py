# -*- coding: utf-8 -*-
import logging
import os

from openerp.addons.base.maintenance.migrations import util
from openerp.tools.safe_eval import safe_eval

NS = 'openerp.addons.base.maintenance.migrations.base.saas~11.'
_logger = logging.getLogger(NS + __name__)

try:
    integer_types = (int, long)
except NameError:
    # python3
    integer_types = (int,)

def str2tuple(s):
    return safe_eval('tuple(%s)' % (s or ''))

def migrate(cr, version):
    cr.execute("DROP TABLE ir_autovacuum")   # should always have been a abstract model

    # adapt crons methods to be `@api.model`
    crons_to_adapt = [
        ('ir.actions.server', 'run', '_run_actions'),
        ('subscription.subscription', 'model_copy', '_cron_model_copy'),
    ]
    for model, oldf, newf in crons_to_adapt:
        cr.execute("""
            UPDATE ir_cron
               SET function=%s
             WHERE model=%s
               AND function=%s
        """, [newf, model, oldf])

    if os.environ.get('ODOO_MIG_S11_CRONS_VALID'):
        return

    # some cron does not need to be changed but take an int as first parameter without being an id
    crons_to_adapt += [
        ('base.gengo.translations', '', '_sync_request'),
        ('base.gengo.translations', '', '_sync_response'),
    ]

    cr.execute("""
        SELECT id, model, function, args
          FROM ir_cron
         WHERE ARRAY[model, function]::text[] NOT IN %s
    """, [tuple([m, f] for m, _, f in crons_to_adapt)])

    for cid, model, func, args in cr.fetchall():
        args_eval = str2tuple(args)
        if (args_eval and
            (type(args_eval[0]) in integer_types or          # ignore booleans
             (isinstance(args_eval[0], (list, tuple)) and
              all(type(x) in integer_types for x in args_eval[0]))
             )):
            cr.execute("UPDATE ir_cron set active=False WHERE id=%s", (cid,))
            _logger.error('Cron #%s calls env[%r].%s(*%s). Using `id` or `ids` as first argument '
                          'may not works if method is `@api.multi`. Cron have been deactivated.',
                          cid, model, func, args)
