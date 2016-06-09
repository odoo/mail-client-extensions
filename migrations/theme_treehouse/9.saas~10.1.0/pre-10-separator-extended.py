# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    view = util.ref(cr, 'theme_treehouse.s_separator_extended')
    if view:
        cr.execute("UPDATE ir_ui_view SET inherit_id=NULL, mode='primary' WHERE id=%s", [view])
