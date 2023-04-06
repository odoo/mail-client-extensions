# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "quality_point_test_type", "active", "boolean")
    cr.execute("UPDATE quality_point_test_type SET active = true")

    util.create_m2m(cr, "product_product_quality_point_rel", "product_product", "quality_point")
    cr.execute(
        """
        INSERT INTO product_product_quality_point_rel(quality_point_id, product_product_id)
        SELECT qp.id, pp.id
          FROM quality_point qp, product_product pp
         WHERE qp.product_tmpl_id = pp.product_tmpl_id
           AND (qp.product_id IS NULL OR pp.id = qp.product_id)
        """
    )

    util.create_m2m(cr, "quality_point_stock_picking_type_rel", "quality_point", "stock_picking_type")
    cr.execute(
        """
            INSERT INTO quality_point_stock_picking_type_rel(quality_point_id, stock_picking_type_id)
                 SELECT id, picking_type_id
                   FROM quality_point
    """
    )

    util.update_field_usage(cr, "quality.point", "product_id", "product_ids")
    util.update_field_usage(cr, "quality.point", "picking_type_id", "picking_type_ids")

    util.remove_field(cr, "quality.point", "product_id")
    util.remove_field(cr, "quality.point", "product_tmpl_id")
    util.remove_field(cr, "quality.point", "picking_type_id")

    util.create_m2m(cr, "quality_alert_stage_quality_alert_team_rel", "quality_alert_stage", "quality_alert_team")

    util.create_column(cr, "quality_check", "additional_note", "text")
