# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "quality_check", "next_check_id", "int4")
    util.create_column(cr, "quality_check", "previous_check_id", "int4")

    # order used in 13.0
    """
    def sort_quality_checks(check):
        # Useful tuples to compute the order
        parent_point_sequence = (check.parent_id.point_id.sequence, check.parent_id.point_id.id)
        point_sequence = (check.point_id.sequence, check.point_id.id)
        # Parent quality checks are sorted according to the sequence number of their associated quality point,
        # with chronological order being the tie-breaker.
        if check.point_id and not check.parent_id:
            score = (0, 0) + point_sequence + (0, 0)
        # Children steps follow their parents, honouring their quality point sequence number,
        # with chronological order being the tie-breaker.
        elif check.point_id:
            score = (0, 0) + parent_point_sequence + point_sequence
        # Checks without points go at the end and are ordered chronologically
        elif not check.parent_id:
            score = (check.id, 0, 0, 0, 0, 0)
        # Children without points follow their respective parents, in chronological order
        else:
            score = (check.parent_id.id, check.id, 0, 0, 0, 0)
        return score
    """

    cr.execute(
        """
        WITH sorted_checks AS (
            SELECT k.id,
                   k.workorder_id,
                   ROW_NUMBER() OVER(PARTITION BY k.workorder_id ORDER BY

                    -- same algorithm as `sort_quality_checks`
                     CASE WHEN t.sequence IS NOT NULL
                            THEN 0
                            ELSE COALESCE(p.id, k.id)
                     END,
                     CASE WHEN t.sequence IS NOT NULL
                            THEN 0
                            ELSE CASE WHEN p.id IS NULL THEN 0 ELSE k.id END
                     END,
                     COALESCE(u.sequence, t.sequence, 0),
                     COALESCE(u.id, t.id, 0),
                     CASE WHEN p.id IS NOT NULL AND t.id IS NOT NULL THEN t.sequence ELSE 0 END,
                     CASE WHEN p.id IS NOT NULL AND t.id IS NOT NULL THEN t.id ELSE 0 END

                   ) as seq
             FROM quality_check k
             JOIN mrp_workorder w ON w.id = k.workorder_id
        LEFT JOIN quality_point t ON t.id = k.point_id
        LEFT JOIN quality_check p ON p.id = k.parent_id
        LEFT JOIN quality_point u ON u.id = p.parent_id
        ),
        linked_checks AS (
            SELECT id,
                   LAG(id) OVER (PARTITION BY workorder_id ORDER BY seq) as prev,
                   LEAD(id) OVER (PARTITION BY workorder_id ORDER BY seq) as next,
                   workorder_id
              FROM sorted_checks
        )
        UPDATE quality_check q
           SET next_check_id = l.next,
               previous_check_id = l.prev
          FROM linked_checks l
         WHERE l.id = q.id
    """
    )

    util.remove_field(cr, "quality.check", "parent_id")
