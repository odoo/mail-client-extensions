# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.force_noupdate(cr, 'web.assets_common', False)
    util.force_noupdate(cr, 'web.assets_backend', False)
