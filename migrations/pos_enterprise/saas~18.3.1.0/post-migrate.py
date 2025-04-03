from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        WITH ranked_stages AS (
            SELECT
                ps.prep_display_id,
                ps.id AS stage_id,
                ROW_NUMBER() OVER (
                    PARTITION BY ps.prep_display_id
                    ORDER BY
                        CASE
                            WHEN ps.sequence IS NOT NULL AND ps.sequence != 0 THEN ps.sequence
                            ELSE ps.id
                        END DESC
                ) AS rank
            FROM
                pos_prep_stage ps
            )
        DELETE FROM pos_preparation_display_order_stage os
        USING ranked_stages rs
        WHERE
            os.preparation_display_id = rs.prep_display_id
            AND os.stage_id <> rs.stage_id
            AND os.done = true
            AND rs.rank = 1;
        """
    )
    cr.execute(
        """
        INSERT INTO pos_prep_state (prep_line_id, todo, stage_id, create_uid, write_uid, create_date, write_date)
        SELECT
            ol.id AS prep_line_id,
            CASE
                WHEN os.done = TRUE THEN FALSE
                ELSE ol.todo
            END AS todo,
            os.stage_id AS stage_id,
            os.create_uid AS create_uid,
            os.write_uid AS write_uid,
            os.create_date AS create_date,
            os.write_date AS write_date
        FROM
            pos_preparation_display_order_stage os
        JOIN
            pos_prep_line ol ON os.order_id = ol.prep_order_id;

        """
    )

    util.remove_field(cr, "pos.prep.line", "todo")
    util.remove_model(cr, "pos_preparation_display.order.stage")
