# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    env = util.env(cr)
    nl_id = env.ref('base.nl').id
    state_codes = ['DR', 'FL', 'FR', 'GE', 'GR', 'LI', 'NB',
                   'NH', 'OV', 'UT', 'ZE', 'ZH', 'BQ1', 'BQ2',
                   'BQ3']
    states = [
        ('l10n_nl.state_nl_%s' % code.lower(), 'res.country.state', {'country_id': nl_id, 'code': code}) for code in state_codes
    ]
    
    for state in states:
        util.ensure_xmlid_match_record(cr, *state)

    
