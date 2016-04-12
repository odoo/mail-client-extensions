# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    pkg = 'FLY COY NCY PAL DBL BOX'.split()

    case = 'CASE ' + ' '.join(
        cr.mogrify('WHEN dhl_package_type=%s THEN %s',
                   [p, util.ref(cr, 'delivery_dhl.dhl_packaging_' + p)])
        for p in pkg
    ) + ' ELSE NULL END'

    cr.execute("""
        UPDATE delivery_carrier
           SET dhl_default_packaging_id = {case}
         WHERE delivery_type = 'dhl'
    """.format(case=case))
