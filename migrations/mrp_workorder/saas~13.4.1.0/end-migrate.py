# -*- coding: utf-8 -*-


def migrate(cr, version):
    # recompute the quality_point_ids of mrp.workorder
    cr.execute("DELETE FROM mrp_workorder_quality_point_rel")
    cr.execute(
        """
        INSERT INTO mrp_workorder_quality_point_rel (mrp_workorder_id, quality_point_id)
             SELECT wo.id AS mrp_workorder_id, qp.id AS quality_point_id
               FROM mrp_workorder AS wo
                    JOIN quality_point AS qp ON qp.operation_id = wo.operation_id
        """
    )
