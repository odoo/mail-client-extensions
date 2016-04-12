# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    pkg = '01 02 03 04 21 24 25 30 2a 2b 2c'.split()

    case = 'CASE ' + ' '.join(
        cr.mogrify('WHEN ups_package_type=%s THEN %s',
                   [p, util.ref(cr, 'delivery_ups.ups_packaging_' + p)])
        for p in pkg
    ) + ' ELSE NULL END'

    cr.execute("""
        UPDATE delivery_carrier
           SET ups_default_packaging_id = {case}
         WHERE delivery_type = 'ups'
    """.format(case=case))
