from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'stock_picking', 'reception_to_invoice', 'boolean')
    cr.execute("""\
        UPDATE  stock_picking
        SET     reception_to_invoice = EXISTS (
            SELECT  1
            FROM    stock_move
            JOIN    purchase_order_line
            ON      purchase_order_line.id = stock_move.purchase_line_id
            JOIN    purchase_order
            ON      purchase_order.id = purchase_order_line.order_id
            AND     purchase_order.invoice_method = 'picking'
            WHERE   stock_move.picking_id = stock_picking.id
        );
        """)
