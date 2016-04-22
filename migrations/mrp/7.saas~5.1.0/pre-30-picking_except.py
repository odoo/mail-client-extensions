# -*- coding: utf-8 -*-

def migrate(cr, version):
    # Cancel moves that are related to Manufacturing Orders of picking_except state
    # Note: this state furtively happen in saas~4. These queries should be a no-op in most cases.
    cr.execute("""
        UPDATE stock_move m
           SET state = 'cancel'
          FROM mrp_production p
         WHERE p.state = 'picking_except'
           AND (m.raw_material_production_id = p.id OR m.production_id = p.id)
    """)
    cr.execute("UPDATE mrp_production SET state = 'cancel' WHERE state = 'picking_except'")
