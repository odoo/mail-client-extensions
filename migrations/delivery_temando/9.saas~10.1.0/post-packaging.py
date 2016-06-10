# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    pkg = {
        x: util.ref(cr, 'delivery_temando.temando_packaging_' + x)
        for x in 'Box Carton Letter Pallet Parcel'.split()
    }
    pkg['Document Envelope'] = util.ref(cr, 'delivery_temando.temando_packaging_Document_Envelope')
    pkg['Satchel/Bag'] = util.ref(cr, 'delivery_temando.temando_packaging_SatchelBag')
    pkg['Unpackage or N/A'] = util.ref(cr, 'delivery_temando.temando_packaging_Unpackage')

    case = 'CASE ' + ' '.join(
        cr.mogrify('WHEN temando_default_packaging_type=%s THEN %s',
                   [p, r])
        for p, r in pkg.items()
    ) + ' ELSE NULL END'

    cr.execute("""
        UPDATE delivery_carrier
           SET temando_default_packaging_id = {case}
         WHERE delivery_type = 'temando'
    """.format(case=case))
