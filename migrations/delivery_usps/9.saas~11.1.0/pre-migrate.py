# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.force_noupdate(cr, 'delivery_usps.usps_partner', True)       # keep it

    cr.execute("""
        UPDATE delivery_carrier
           SET usps_service = 'First-Class'
         WHERE usps_service = 'First Class'     -- note the hyphen
    """)
