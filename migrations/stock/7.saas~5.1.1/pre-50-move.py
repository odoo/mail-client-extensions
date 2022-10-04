from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    """
    As product_qty will become a function field, the old value should be in product_uom_qty
    The lots of a stock move can still be used with restrict_lot_id
    Inventory and stock moves are related with a one2many instead of many2many in v8
    The invoice_state needs to be copied from the picking on the move
    """
    util.rename_field(cr, "stock.move", "product_qty", "product_uom_qty")
    util.rename_field(cr, "stock.move", "prodlot_id", "restrict_lot_id")

    # now bootstrap the new function field
    util.create_column(cr, "stock_move", "product_qty", "numeric")
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
            UPDATE  stock_move move
            SET     product_qty
                    = round(move.product_uom_qty * puom.factor / muom.factor,
                            ceil(-log(puom.rounding))::integer)
            FROM    product_product prod
            ,       product_uom muom
            ,       product_template temp
            ,       product_uom puom
            WHERE   prod.id = move.product_id
            AND     temp.id = prod.product_tmpl_id
            AND     muom.id = move.product_uom
            AND     puom.id = temp.uom_id
            """,
            table="stock_move",
            alias="move",
        ),
    )

    # For inventories, we need to change the many2many to many2one for correcting the moves
    util.rename_field(cr, "stock.inventory.line", "product_uom", "product_uom_id")
    util.create_column(cr, "stock_move", "inventory_id", "int4")
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
            UPDATE stock_move
            SET inventory_id = inv.id
            FROM stock_inventory inv, stock_inventory_move_rel invmove
            WHERE invmove.move_id = stock_move.id AND invmove.inventory_id = inv.id
            """,
            table="stock_move",
            alias="stock_move",
        ),
    )

    util.create_column(cr, "stock_move", "invoice_state", "varchar")
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
            UPDATE stock_move
            SET invoice_state = pick.invoice_state
            FROM stock_picking pick
            WHERE pick.id = stock_move.picking_id
            """,
            table="stock_move",
            alias="stock_move",
        ),
    )
