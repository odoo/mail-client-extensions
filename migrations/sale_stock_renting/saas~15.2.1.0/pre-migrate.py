# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("ALTER TABLE rental_reserved_lot_rel RENAME COLUMN stock_production_lot_id TO stock_lot_id")
    cr.execute("ALTER TABLE rental_pickedup_lot_rel RENAME COLUMN stock_production_lot_id TO stock_lot_id")
    cr.execute("ALTER TABLE rental_returned_lot_rel RENAME COLUMN stock_production_lot_id TO stock_lot_id")
    cr.execute(
        "ALTER TABLE rental_wizard_stock_production_lot_rel RENAME COLUMN stock_production_lot_id TO stock_lot_id"
    )

    cr.execute("ALTER TABLE wizard_pickedup_serial RENAME COLUMN stock_production_lot_id TO stock_lot_id")
    cr.execute("ALTER TABLE wizard_returned_serial RENAME COLUMN stock_production_lot_id TO stock_lot_id")
