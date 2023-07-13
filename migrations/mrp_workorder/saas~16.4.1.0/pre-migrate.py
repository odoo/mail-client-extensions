# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mrp.workcenter", "allow_employee")
    util.remove_field(cr, "mrp.workorder", "allow_employee")

    util.remove_view(cr, "mrp_workorder.mrp_routing_workcenter_form_view_inherit")
    util.remove_view(cr, "mrp_workorder.mrp_workcenter_tree_view_inherit")
    util.remove_view(cr, "mrp_workorder.mrp_production_workorder_tree_editable_view_connect")
    util.remove_view(cr, "mrp_workorder.mrp_production_workorder_tree_editable_view_inherit_workorder_hr")
    util.remove_view(cr, "mrp_workorder.mrp_workorder_view_kanban")
    util.remove_view(cr, "mrp_workorder.mrp_workorder_view_form_inherit_workorder_hr")
    util.remove_view(cr, "mrp_workorder.mrp_workorder_view_tablet_form_inherit_workorder_hr")
