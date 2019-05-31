# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("""
        CREATE table stock_putaway_rule (
            id SERIAL NOT NULL PRIMARY KEY,
            create_uid integer,
            create_date timestamp without time zone,
            write_uid integer,
            write_date timestamp without time zone,
            product_id int4,
            category_id int4,
            location_in_id int4,
            location_out_id int4,
            sequence int4
        )
    """)
    cr.execute("""
        INSERT INTO stock_putaway_rule (product_id,category_id,location_in_id,location_out_id,sequence)
            SELECT sfps.product_id, sfps.category_id, s.id, sfps.fixed_location_id, sfps.sequence
              FROM stock_fixed_putaway_strat sfps
        INNER JOIN product_putaway p on sfps.putaway_id=p.id
        INNER JOIN stock_location s on p.id=s.putaway_strategy_id
    """)
    util.remove_model(cr, "product.putaway")
    util.remove_model(cr, "stock.fixed.putaway.strat")
    util.remove_field(cr, "stock.location", "putaway_strategy_id")
