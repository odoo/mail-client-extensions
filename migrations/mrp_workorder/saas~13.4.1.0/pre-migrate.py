from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "quality_point", "old_id", "int4")  # Working column
    column_qua = util.get_columns(cr, "quality_point", ignore=("id", "old_id", "operation_id"))
    # A quality point was link to a operation, then we need to duplicate also quality point for each operation
    # duplicate (for each operation) related to ...
    # => point_id of quality_point update via production_id.bom_id
    cr.execute(
        util.format_query(
            cr,
            """
        WITH quality_point_by_new_op AS (
            SELECT {column_qua_pre}, quality_point_by_new_op.id AS old_id, temp_new_mrp_operation.id AS operation_id
               FROM quality_point quality_point_by_new_op
                    JOIN temp_new_mrp_operation ON quality_point_by_new_op.operation_id = temp_new_mrp_operation.old_id
                    JOIN mrp_bom bom ON temp_new_mrp_operation.bom_id = bom.id
                    JOIN product_product_quality_point_rel rel ON rel.quality_point_id = quality_point_by_new_op.id
                    JOIN product_product pp ON pp.id = rel.product_product_id
               WHERE rel.product_product_id = bom.product_id
               OR pp.product_tmpl_id = bom.product_tmpl_id

        ),
        inserted_quality_point AS (
            INSERT INTO quality_point ({column_qua}, old_id, operation_id)
            SELECT {column_qua_pre}, old_id, operation_id
              FROM quality_point_by_new_op
         RETURNING id, old_id, operation_id
        ),
        update_quality_check AS (
            UPDATE quality_check
               SET point_id = inserted_quality_point.id,
                   production_id = mrp_workorder.production_id
              FROM mrp_production
                   JOIN mrp_workorder ON mrp_production.id = mrp_workorder.production_id
                   JOIN mrp_bom ON mrp_production.bom_id = mrp_bom.id
                   JOIN temp_new_mrp_operation ON mrp_bom.id = temp_new_mrp_operation.bom_id
                   JOIN inserted_quality_point ON inserted_quality_point.operation_id = temp_new_mrp_operation.id
             WHERE quality_check.point_id = inserted_quality_point.old_id
                   AND quality_check.workorder_id = mrp_workorder.id
        ),
        inserted_m2m_product_ids AS (
            INSERT INTO product_product_quality_point_rel (quality_point_id, product_product_id)
            SELECT inserted_quality_point.id, product_product_quality_point_rel.product_product_id
              FROM inserted_quality_point
                   JOIN product_product_quality_point_rel
                        ON inserted_quality_point.old_id = product_product_quality_point_rel.quality_point_id
        )
        INSERT INTO quality_point_stock_picking_type_rel (quality_point_id, stock_picking_type_id)
        SELECT inserted_quality_point.id, quality_point_stock_picking_type_rel.stock_picking_type_id
          FROM inserted_quality_point
               JOIN quality_point_stock_picking_type_rel
                    ON inserted_quality_point.old_id = quality_point_stock_picking_type_rel.quality_point_id
        """,
            column_qua=column_qua,
            column_qua_pre=column_qua.using(alias="quality_point_by_new_op"),
        )
    )

    # Remove old quality point
    cr.execute(
        """
        DELETE FROM quality_point qp
              USING quality_point old
              WHERE old.old_id = qp.id
        """
    )

    util.remove_column(cr, "quality_point", "old_id")
    util.fixup_m2m(cr, "quality_point_product_product_rel", "quality_point", "product_product")
    util.fixup_m2m(cr, "quality_point_stock_picking_type_rel", "quality_point", "stock_picking_type")

    util.remove_field(cr, "quality.point", "routing_ids")
    util.remove_field(cr, "quality.point", "routing_id")
    util.remove_field(cr, "mrp.workorder", "workorder_line_id")

    util.create_column(cr, "quality_check", "move_id", "int4")
    util.create_column(cr, "quality_check", "move_line_id", "int4")
    # Fill move_id with the move_id of related mrp_workorder_line
    cr.execute(
        """
        UPDATE quality_check AS qc
           SET move_id = mwl.move_id
          FROM mrp_workorder_line AS mwl
         WHERE qc.workorder_line_id = mwl.id
        """
    )
    cr.execute(
        """
        UPDATE quality_check AS qc
           SET production_id = mw.production_id
          FROM mrp_workorder AS mw
         WHERE mw.id = qc.workorder_id
        """
    )
    util.remove_field(cr, "quality.check", "workorder_line_id")

    util.remove_view(cr, xml_id="mrp_workorder.mrp_workorder_view_tree_inherit_quality")
    util.remove_view(cr, xml_id="mrp_workorder.mrp_routing_view_form_inherit_quality")
