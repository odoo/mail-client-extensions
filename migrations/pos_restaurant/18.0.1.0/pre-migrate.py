from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        """
        UPDATE pos_order
           SET last_order_preparation_change = jsonb_build_object(
                'lines', COALESCE(last_order_preparation_change::jsonb, '{{}}'::jsonb),
                'generalNote', ''
                )
        """,
        table="pos_order",
    )
