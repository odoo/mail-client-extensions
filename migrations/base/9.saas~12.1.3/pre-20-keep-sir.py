# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    sir = util.ref(cr, 'base.res_partner_title_sir')
    if not sir:
        return
    for tbl, col, _, _ in util.get_fk(cr, 'res_partner_title'):
        cr.execute("SELECT count(*) FROM {tbl} WHERE {col}=%s".format(**locals()), [sir])
        if cr.fetchone()[0]:
            # title used -> keep it
            util.force_noupdate(cr, 'base.res_partner_title_sir', True)
            break
    else:   # no break
        util.remove_record(cr, 'base.res_partner_title_sir')
