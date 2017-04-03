# -*- coding: utf-8 -*-
from itertools import chain
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):

    states = 'draft confirmed announced published refused cancel'.split()
    mapping = {s: util.ref(cr, 'website_event_track.event_track_stage%d' % i)
               for i, s in enumerate(states)}

    whens = 'WHEN state=%s THEN %s ' * len(states)
    values = list(chain(*mapping.items()))

    cr.execute("""
        UPDATE event_track
           SET stage_id = CASE {0} ELSE %s END
    """.format(whens), values + [mapping['draft']])

    util.remove_field(cr, 'event.track', 'state')
    # add uniq constraint
    util.env(cr)['event.track']._add_sql_constraints()
