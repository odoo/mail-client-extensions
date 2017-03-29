# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        UPDATE base_automation a
           SET filter_pre_domain = f.domain
          FROM ir_filters f
         WHERE f.id = a.filter_pre_id
    """)
    cr.execute("""
        UPDATE base_automation a
           SET filter_domain = f.domain
          FROM ir_filters f
         WHERE f.id = a.filter_id
    """)

    util.remove_field(cr, 'base.automation', 'filter_pre_id')
    util.remove_field(cr, 'base.automation', 'filter_id')
