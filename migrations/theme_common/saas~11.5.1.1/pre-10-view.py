# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    views = util.splitlines("""
        theme_common.assets_frontend
    """)

    for v in views:
        util.remove_view(cr, v)

    # nearly all options have changed structure, but some were simply removed and listing all of them is gonna take ages
    # delete them all and let the update do the rest
    cr.execute("SELECT module,name FROM ir_model_data WHERE model='ir.ui.view' AND module like '%theme%' and name like 'option_%'")
    for v in cr.dictfetchall():
        util.remove_view(cr, '.'.join([v['module'], v['name']]))
