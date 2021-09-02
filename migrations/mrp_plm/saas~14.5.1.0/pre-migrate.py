# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "mrp_document", "origin_attachment_id", "int4")
    util.create_column(cr, "mrp_eco_routing_change", "operation_id", "int4")
    util.create_column(cr, "mrp_eco_stage", "legend_blocked", "varchar", default="Blocked")
    util.create_column(cr, "mrp_eco_stage", "legend_done", "varchar", default="Ready")
    util.create_column(cr, "mrp_eco_stage", "legend_normal", "varchar", default="In Progress")
    util.create_column(cr, "mrp_eco_stage", "description", "text")

    util.create_m2m(cr, "mrp_eco_stage_type_rel", "mrp_eco_type", "mrp_eco_stage", "type_id", "stage_id")
    cr.execute(
        """
        INSERT INTO mrp_eco_stage_type_rel(type_id, stage_id)
             SELECT type_id, id
               FROM mrp_eco_stage
              WHERE type_id IS NOT NULL
    """
    )
    util.remove_column(cr, "mrp_eco_stage", "type_id")
    util.rename_field(cr, "mrp.eco.stage", "type_id", "type_ids")
    util.remove_view(cr, "mrp_plm.report_mrp_operation_line_inherit_mrp_plm")
    util.remove_view(cr, "mrp_plm.report_mrp_byproduct_line_inherit_mrp_plm")
    util.remove_view(cr, "mrp_plm.product_template_view_form_inherit_version_plm")
