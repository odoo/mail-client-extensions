# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    views = util.splitlines("""
        theme_common.assets_frontend
    """)

    for v in views:
        util.remove_view(cr, v)
        
