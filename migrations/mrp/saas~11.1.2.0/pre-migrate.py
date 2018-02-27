# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    util.remove_field(cr, 'res.config.settings', 'module_quality_mrp')   # rename to mrp_workorder?
    util.rename_xmlid(cr, *eb('mrp.action_mrp_unbuild_{moves,move_line}'))
    util.force_noupdate(cr, 'mrp.picking_type_manufacturing', True)
