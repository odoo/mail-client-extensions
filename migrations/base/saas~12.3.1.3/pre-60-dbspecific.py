# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def _openerp(cr, version):
    util.remove_view(cr, view_id=12236)

def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _openerp,
    })
