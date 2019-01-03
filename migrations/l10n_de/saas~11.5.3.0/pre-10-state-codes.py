# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    env = util.env(cr)
    de_id = env.ref('base.de').id
    state_codes = ['BW', 'BY', 'BE', 'BB', 'HB', 'HH', 'HE',
                   'MV', 'NI', 'NW', 'RP', 'SL', 'SN', 'ST',
                   'SH', 'TH']
    states = [
        ('l10n_de.state_de_%s' % code.lower(), 'res.country.state', {'country_id': de_id, 'code': code}) for code in state_codes
    ]
    
    for state in states:
        util.ensure_xmlid_match_record(cr, *state)

    
