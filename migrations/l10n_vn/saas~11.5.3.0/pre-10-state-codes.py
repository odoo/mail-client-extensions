# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    env = util.env(cr)
    vn_id = env.ref('base.vn').id
    state_codes = ['VN-44', 'VN-57', 'VN-31', 'VN-54', 'VN-53', 'VN-55',
                   'VN-56', 'VN-58', 'VN-43', 'VN-40', 'VN-50', 'VN-04',
                   'VN-59', 'VN-CT', 'VN-71', 'VN-33', 'VN-DN', 'VN-39',
                   'VN-72', 'VN-45', 'VN-30', 'VN-14', 'VN-SG', 'VN-61',
                   'VN-73', 'VN-03', 'VN-HN', 'VN-63', 'VN-HP', 'VN-23',
                   'VN-66', 'VN-47', 'VN-34', 'VN-28', 'VN-41', 'VN-02',
                   'VN-01', 'VN-35', 'VN-09', 'VN-22', 'VN-18', 'VN-67',
                   'VN-36', 'VN-68', 'VN-32', 'VN-24', 'VN-13', 'VN-27',
                   'VN-29', 'VN-25', 'VN-05', 'VN-52', 'VN-20', 'VN-46',
                   'VN-21', 'VN-69', 'VN-37', 'VN-07', 'VN-26', 'VN-51',
                   'VN-49', 'VN-70', 'VN-06']
    states = [
        ('l10n_vn.state_vn_%s' % code.lower(), 'res.country.state', {'country_id': vn_id, 'code': code}) for code in state_codes
    ]
    
    for state in states:
        util.ensure_xmlid_match_record(cr, *state)

    
