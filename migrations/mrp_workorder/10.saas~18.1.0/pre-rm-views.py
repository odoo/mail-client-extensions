# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'mrp_workorder.mrp_workcenter_view_kanban_inherit_panel', deactivate_custom=True)
    util.remove_view(cr, 'mrp_workorder.mrp_workorder_assets_backend', deactivate_custom=True)
    util.remove_view(cr, 'mrp_workorder.mrp_workorder_view_form_tablet', deactivate_custom=True)

    util.remove_record(cr, 'mrp_workorder.mrp_workorder_action_tablet')
