# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "mrp_production", "product_uom_qty", "float8")
    util.create_column(cr, "mrp_workcenter_productivity_loss", "loss_id", "int4")
    util.create_column(cr, "stock_warehouse", "pbm_mto_pull_id", "int4")
    util.create_column(cr, "stock_warehouse", "sam_rule_id", "int4")
    util.create_column(cr, "stock_warehouse", "pbm_type_id", "int4")
    util.create_column(cr, "stock_warehouse", "sam_type_id", "int4")
    util.create_column(cr, "stock_warehouse", "pbm_route_id", "int4")
    util.create_column(cr, "stock_warehouse", "pbm_loc_id", "int4")
    util.create_column(cr, "stock_warehouse", "sam_loc_id", "int4")
    util.create_column(cr, "stock_warehouse", "manufacture_steps", "varchar")

    cr.execute("UPDATE stock_warehouse SET manufacture_steps='mrp_one_step'")

    util.rename_xmlid(cr, "mrp.product_template_search_view_procurment", "mrp.mrp_product_template_search_view")
    util.rename_xmlid(cr, "mrp.view_mrp_product_product_form_inherited_view", "mrp.mrp_product_product_search_view")
    util.rename_xmlid(cr, "mrp.view_warehouse_inherited", "mrp.view_warehouse_inherit_mrp")

    util.remove_field(cr, "product.template", "mo_count")
    util.remove_field(cr, "product.product", "mo_count")
