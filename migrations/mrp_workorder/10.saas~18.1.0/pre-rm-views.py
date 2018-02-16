# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'mrp_workorder.mrp_workcenter_view_kanban_inherit_panel')
    util.remove_view(cr, 'mrp_workorder.mrp_workorder_assets_backend')
    util.remove_view(cr, 'mrp_workorder.mrp_workorder_view_form_tablet')

    util.remove_record(cr, 'mrp_workorder.mrp_workorder_action_tablet')
