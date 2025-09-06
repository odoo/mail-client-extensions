from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "stock_picking_type", "dispatch_management", "boolean", default=False)

    cr.execute("""
        UPDATE stock_picking_type
           SET dispatch_management = True
        WHERE id IN (
            SELECT out_type_id FROM stock_warehouse
             UNION
            SELECT in_type_id FROM stock_warehouse
             UNION
            SELECT pick_type_id FROM stock_warehouse WHERE delivery_steps = 'pick_pack_ship'
             UNION
            SELECT pack_type_id FROM stock_warehouse WHERE delivery_steps = 'pick_ship'
        );
    """)
