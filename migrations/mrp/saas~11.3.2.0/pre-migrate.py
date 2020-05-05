# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "mrp.mrp_bom_cost_report")
    util.remove_record(cr, "mrp.action_report_bom_price")
    util.remove_model(cr, "report.mrp.mrp_bom_cost_report")
    util.remove_view(cr, "mrp.mrp_bom_structure_report")
    util.remove_record(cr, "mrp.action_report_bom_structure")
    util.remove_model(cr, "report.mrp.mrp_bom_structure_report")

    util.remove_view(cr, "mrp.mrp_bom_component_tree_view")
    util.remove_view(cr, "mrp.view_mrp_bom_line_filter")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("mrp.access_{product,uom}_uom_user"))
    util.rename_xmlid(cr, "mrp.access_product_puom_categ", "mrp.access_uom_category")
    util.rename_xmlid(cr, *eb("mrp.access_{product_uom_categ,uom_category}_mrp_manager"))
    util.rename_xmlid(cr, *eb("mrp.access_{product,uom}_uom_mrp_manager"))

    util.rename_xmlid(cr, *eb("mrp.mrp_production_work{center,order}_tree_view_inherit"))
    util.rename_xmlid(cr, *eb("mrp.mrp_production_work{center,order}_form_view_inherit"))
    util.rename_xmlid(cr, *eb("mrp.mrp_production_work{center,order}_form_view_filter"))

    util.move_field_to_module(cr, "mrp.workcenter", "costs_hour", "mrp_account", "mrp")
