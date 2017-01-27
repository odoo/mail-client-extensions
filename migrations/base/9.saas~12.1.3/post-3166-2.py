# -*- coding: utf-8 -*-
import logging
from collections import defaultdict
import csv
import difflib
import os
import pprint

from openerp.tools import ustr
from openerp.addons.base.maintenance.migrations import util

HERE = os.path.dirname(os.path.realpath(__file__))
NS = 'openerp.addons.base.maintenance.migrations.base.saas~12.'
_logger = logging.getLogger(NS + __name__)

MIN_DISTANCE_LEVEL = 80

def distance(a, b):
    return int(100 * difflib.SequenceMatcher(None, ustr(a), ustr(b)).ratio())

def migrate(cr, version):
    # 1. remove all unused (without xid)

    # NOTE: UNION act as a GROUP BY
    used_states = ' UNION '.join(
        'SELECT {1} AS id FROM {0} WHERE {1} IS NOT NULL'.format(tbl, col)
        for tbl, col, _, _ in util.get_fk(cr, 'res_country_state')
    )
    if used_states:
        used_states += ' UNION '
    used_states += """
        SELECT res_id AS id
          FROM ir_model_data
         WHERE model = 'res.country.state'
           AND COALESCE(module, '') NOT IN ('', '__export__')
    """

    cr.execute("DELETE FROM res_country_state WHERE id NOT IN ({0})".format(used_states))
    cr.execute("""
        DELETE FROM ir_model_data
              WHERE model = 'res.country.state'
                AND res_id NOT IN (SELECT id FROM res_country_state)
    """)

    # load data
    cr.execute("""
        SELECT s.id, c.code, s.name
          FROM res_country_state s
          JOIN res_country c ON (c.id = s.country_id)
         WHERE NOT EXISTS(SELECT 1
                            FROM ir_model_data
                           WHERE model='res.country.state'
                             AND COALESCE(module, '') NOT IN ('', '__export__')
                             AND res_id = s.id
                          )
    """)
    todel = []
    current_states = cr.fetchall()
    if current_states:
        states_matches = defaultdict(list)
        with open(os.path.join(HERE, 'states.csv')) as fp:
            reader = csv.reader(fp)
            reader.next()   # remove header line
            states = list(iter(reader))

        for s in states:
            # s = (country, badname, xid, namereplace, codereplace)
            states_matches[s[0]].append(s)

        # match against states from modules
        cr.execute("""
            SELECT c.code, s.name, x.module || '.' || x.name
              FROM res_country_state s
              JOIN res_country c ON (c.id = s.country_id)
              JOIN ir_model_data x ON (x.model = 'res.country.state' AND x.res_id = s.id)
             WHERE COALESCE(x.module, '') NOT IN ('', '__export__')
        """)
        for c, s, x in cr.fetchall():
            states_matches[c].append((c, s, x, '', ''))

        for sid, country, name in current_states:
            dist = sorted(((distance(name.lower(), x[1].lower()), x)
                           for x in states_matches[country]),
                          reverse=True)

            for d, s in dist:
                if d > MIN_DISTANCE_LEVEL:
                    todel.append(sid)
                    _logger.debug('replace state: %s %s -> %s (%s%%)', country, name, s[2], d)
                    util.replace_record_references(cr,
                                                   ('res.country.state', sid),
                                                   ('res.country.state', util.ref(cr, s[2])),
                                                   replace_xmlid=False,
                                                   )
                    break
    if todel:
        util.env(cr)['res.country.state'].browse(todel).unlink()
    todel = []

    # search duplicates
    cr.execute("""
        SELECT c.code, s.code, array_agg(s.name ORDER BY s.id DESC), array_agg(s.id ORDER BY s.id DESC)
          FROM res_country_state s
          JOIN res_country c ON (c.id = s.country_id)
      GROUP BY c.code, s.code
        HAVING count(s.id) > 1
    """)
    dups = cr.fetchall()
    for country, code, states, ids in dups:
        i = 0
        while len(states) > i + 1:
            cs = states[i]
            j = len(states) - 1
            while j > i:
                if distance(cs, states[j]) > MIN_DISTANCE_LEVEL or (states[j].lower() == code.lower()):
                    todel.append(ids[j])
                    util.replace_record_references(cr,
                                                   ('res.country.state', ids[j]),
                                                   ('res.country.state', ids[i]),
                                                   replace_xmlid=False,
                                                   )
                    del states[j]
                    del ids[j]
                j -= 1
            i += 1

    dups = [d for d in dups if len(d[2]) > 1]
    if dups:
        _logger.warning('Duplicated states:\n%s', pprint.pformat(dups))

    if todel:
        util.env(cr)['res.country.state'].browse(todel).unlink()

    # Try to set the constraint
    cr.commit()     # adding contraint may fail and will rollback
    util.env(cr)['res.country.state']._add_sql_constraints()
