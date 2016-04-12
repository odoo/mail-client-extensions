# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    pkg = 'FEDEX_BOX FEDEX_10KG_BOX FEDEX_25KG_BOX FEDEX_ENVELOPE FEDEX_PAK FEDEX_TUBE YOUR_PACKAGING'.split()

    case = 'CASE ' + ' '.join(
        cr.mogrify('WHEN fedex_package_type=%s THEN %s',
                   [p, util.ref(cr, 'delivery_fedex.fedex_packaging_' + p)])
        for p in pkg
    ) + ' ELSE NULL END'

    cr.execute("""
        UPDATE delivery_carrier
           SET fedex_default_packaging_id = {case}
         WHERE delivery_type = 'fedex'
    """.format(case=case))
