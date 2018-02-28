# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'mrp.workorder', 'maintenance_request_count')
    util.remove_view(cr, 'mrp_maintenance.mrp_workorder_view_form_inherit_maintenance')
