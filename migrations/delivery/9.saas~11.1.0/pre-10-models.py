# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'delivery_carrier', 'integration_level', 'varchar')
    cr.execute("""
        UPDATE delivery_carrier
           SET integration_level = CASE WHEN shipping_enabled THEN 'rate_and_ship'
                                   ELSE 'rate'
                                   END
    """)
