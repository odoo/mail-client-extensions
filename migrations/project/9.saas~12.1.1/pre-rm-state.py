# -*- coding: utf-8 -*-
import logging

from openerp.addons.base.maintenance.migrations import util
from openerp.tools.safe_eval import safe_eval
import openerp.osv.expression as exp

NS = 'openerp.addons.base.maintenance.migrations.base.9.'
_logger = logging.getLogger(NS + __name__)

evaluation_context = {
    'uid': util.SelfPrint('uid'),
    'user': util.SelfPrint('user'),
    'current_date': util.SelfPrint('current_date'),
    'datetime': util.SelfPrint('datetime'),
    'context_today': util.SelfPrint('context_today'),
}


def adapt_filters(cr, model, prefix=None):
    lvalue = '%s.state' % prefix if prefix else 'state'
    cr.execute("""SELECT id, domain
                    FROM ir_filters
                   WHERE domain like %s
                     AND model_id = %s
               """, ['%' + lvalue + '%', model])

    for fid, domain in cr.fetchall():
        try:
            eval_dom = safe_eval(domain, evaluation_context)
        except Exception:
            _logger.warning('Cannot evaluate filter #%s: %r', fid, domain, exc_info=True)
            continue
        final_dom = []
        for element in eval_dom:
            if not exp.is_leaf(element):
                final_dom.append(element)
                continue

            left, operator, right = element = exp.normalize_leaf(element)
            if left == lvalue:
                final_dom.append(exp.TRUE_LEAF)
            else:
                final_dom.append(element)
        _logger.debug('#%s: %r -> %r', fid, domain, final_dom)
        cr.execute("UPDATE ir_filters SET domain=%s WHERE id=%s", (str(final_dom), fid))

def migrate(cr, version):
    cr.execute("""
        UPDATE project_project
           SET active=false
         WHERE state IN ('close', 'cancelled')
    """)

    # adapt filters
    adapt_filters(cr, 'project.project')
    for tbl, col, _, _ in util.get_fk(cr, 'project_project'):
        if not util.column_exists(cr, tbl, "id"):
            # ignore m2m tables
            continue
        model = util.model_of_table(cr, tbl)
        adapt_filters(cr, model, prefix=col)

    util.remove_field(cr, 'project.project', 'state')
