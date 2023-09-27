from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        """
        UPDATE quality_point
           SET testing_percentage_within_lot = 100
         WHERE is_lot_tested_fractionally IS NOT TRUE
        """,
        table="quality_point",
    )
    util.remove_column(cr, "quality_point", "is_lot_tested_fractionally")
