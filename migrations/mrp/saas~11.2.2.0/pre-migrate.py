# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'mrp.workorder', 'tracking')
    util.rename_field(cr, 'res.config.settings', 'module_mrp_repair', 'module_repair')
