# -*- coding: utf-8 -*-

def migrate(cr, version):
    # The structure of the pack operations with lots changed
    # While before a pack operation had 1 lot_id,
    # now a pack operation can have different lots (stock.production.lot) with
    # each its own qty.  This is saved in a stock.pack.operation.lot
    # That is why we need to create a lot by pack operation
    cr.execute("""
        INSERT INTO stock_pack_operation_lot (operation_id, lot_id, qty)
          SELECT id, lot_id, product_qty
            FROM stock_pack_operation WHERE lot_id IS NOT NULL
    """)

    # Before, we had track_incoming, track_outgoing and track_all
    # The difference between those is put on the picking types now,
    # but it makes no sense to try to do something for that in the migration.
    # As a serial number concept did not exist in v8,
    # everything that has some tracking is converted to lot tracking
    cr.execute("""
        UPDATE product_template SET tracking = 'lot'
        WHERE track_incoming = 't' OR
        track_outgoing = 't' OR track_all = 't'
    """)
