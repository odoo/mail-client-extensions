from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "quality_check", "qty_passed", "float")
    util.create_column(cr, "quality_check", "qty_failed", "float")
    util.explode_execute(
        cr,
        """
            UPDATE quality_check qc
            SET qty_passed = CASE
                    WHEN qc.quality_state = 'pass' THEN sml.quantity
                    ELSE 0
                END,
                qty_failed = CASE
                    WHEN qc.quality_state = 'fail' THEN sml.quantity
                    ELSE 0
                END
            FROM stock_move_line sml
            WHERE qc.move_line_id = sml.id
        """,
        table="quality_check",
        alias="qc",
    )
