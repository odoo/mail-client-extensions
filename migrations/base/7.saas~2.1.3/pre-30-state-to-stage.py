# -*- coding: utf-8 -*-
import logging

from openerp.tools import mute_logger
from openerp.tools.safe_eval import safe_eval
import openerp.osv.expression as exp

_logger = logging.getLogger(__name__)

class SelfPrint(object):
    def __init__(self, name):
        self.__name = name

    def __getattr__(self, attr):
        return SelfPrint('%r.%s' % (self, attr))

    def __call__(self, *args, **kwargs):
        s = []
        for a in args:
            s.append(repr(a))
        for k, v in kwargs:
            s.append('%s=%r' % (k, v))
        return SelfPrint('%r(%s)' % (self, ', '.join(s)))

    def __add__(self, other):
        return SelfPrint('%r + %r' % (self, other))

    def __radd__(self, other):
        return SelfPrint('%r + %r' % (other, self))

    def __sub__(self, other):
        return SelfPrint('%r - %r' % (self, other))

    def __rsub__(self, other):
        return SelfPrint('%r - %r' % (other, self))

    def __mul__(self, other):
        return SelfPrint('%r * %r' % (self, other))

    def __rmul__(self, other):
        return SelfPrint('%r * %r' % (other, self))

    def __div__(self, other):
        return SelfPrint('%r / %r' % (self, other))

    def __rdiv__(self, other):
        return SelfPrint('%r / %r' % (other, self))

    def __floordiv__(self, other):
        return SelfPrint('%r // %r' % (self, other))

    def __rfloordiv__(self, other):
        return SelfPrint('%r // %r' % (other, self))

    def __mod__(self, other):
        return SelfPrint('%r % %r' % (self, other))

    def __rmod__(self, other):
        return SelfPrint('%r % %r' % (other, self))

    def __repr__(self):
        return self.__name
    __str__ = __repr__


@mute_logger('openerp.osv.expression')
def migrate(cr, version):
    """On some model, state field has been replace by stage_id.
        ir.filters may still refer to state field
    """

    evaluation_context = {
        'uid': SelfPrint('uid'),
        'user': SelfPrint('user'),
        'current_date': SelfPrint('current_date'),
        'datetime': SelfPrint('datetime'),
        'context_today': SelfPrint('context_today'),
    }

    def domain_of_stage_model(states):
        r = {}
        for s in states:
            r[s] = [(e[0].replace('stage_id.', ''), e[1], e[2]) if exp.is_leaf(e) else e for e in states[s]]
        return r

    models = {
        'crm.lead': {
            'draft': ['&', ('stage_id.probability', '=', 0), ('stage_id.sequence', '<=', 1)],
            'open': ['&', '&', ('stage_id.type', '=', 'opportunity'),
                               ('stage_id.probability', '>', 0), ('stage_id.probability', '<', 100)],
            'pending': ['&', '&', ('stage_id.type', '=', 'opportunity'),
                                  ('stage_id.probability', '>', 0), ('stage_id.probability', '<', 100)],  # same as open
            'done': ['&', ('stage_id.probability', '=', 100), ('stage_id.fold', '=', True)],
            'cancel': ['&', '&', ('stage_id.probability', '=', 0), ('stage_id.fold', '=', True),
                            ('stage_id.sequence', '>', 1)],
        },
        'crm.claim': {
            'draft': [('stage_id.sequence', '<=', 1)],
            'open': [('stage_id.name', 'ilike', 'progress')],
            'done': [('stage_id.name', 'ilike', 'settled')],
            'cancel': [('stage_id.name', 'ilike', 'rejected')],
        },
        'project.task': {
            'draft': [('stage_id.sequence', '<=', 1)],
            'open': ['&', '&', ('stage_id.sequence', '!=', 1),
                          ('stage_id.name', 'not ilike', 'done'), ('stage_id.name', 'not ilike', 'cancelled')],
            'done': [('stage_id.name', 'ilike', 'done')],
            'cancelled': [('stage_id.name', 'ilike', 'cancelled')],
        },
        'hr.applicant': {
            'draft': [('stage_id.sequence', '<=', 1)],
            'open': [('stage_id.name', 'ilike', 'interview')],
            'pending': [('stage_id.name', 'ilike', 'proposed')],
            'done': [('stage_id.name', 'ilike', 'signed')],
            'cancel': [('stage_id.name', 'ilike', 'refused')],
        },

    }
    models['project.issue'] = models['project.task']
    models['crm.case.stage'] = domain_of_stage_model(models['crm.lead'])
    models['crm.claim.stage'] = domain_of_stage_model(models['crm.claim'])
    models['project.task.type'] = domain_of_stage_model(models['project.task'])
    models['hr.recruitment.stage'] = domain_of_stage_model(models['hr.applicant'])

    # now update ir.filters
    cr.execute("""SELECT id, model_id, domain
                    FROM ir_filters
                   WHERE domain like %s
                     AND model_id IN %s
               """, ('%state%', tuple(models.keys())))

    for fid, model, domain in cr.fetchall():
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
            if left not in ['state', 'stage_id.state']:
                final_dom.append(element)
                continue

            if operator not in ['in', 'not in']:
                right = [right]

            new_doms = []
            for state in right:
                try:
                    dom = list(models[model][state])
                except KeyError:
                    continue
                if operator in exp.NEGATIVE_TERM_OPERATORS:
                    dom.insert(0, '!')
                new_doms.append(dom)

            final_dom += ['|'] * (len(new_doms) - 1)
            for d in new_doms:
                final_dom += d

        cr.execute("UPDATE ir_filters SET domain=%s WHERE id=%s", (str(final_dom), fid))
