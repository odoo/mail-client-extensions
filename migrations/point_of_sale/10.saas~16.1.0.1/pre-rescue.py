# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'pos_session', 'rescue', 'boolean')
    cr.execute("""
        UPDATE pos_session
           SET rescue = (name like '%RESCUE FOR%')
         WHERE rescue IS NULL
    """)

    util.create_column(cr, 'pos_config', 'customer_facing_display_html', 'text')
