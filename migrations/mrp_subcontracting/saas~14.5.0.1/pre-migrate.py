from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "mrp_production", "subcontracting_has_been_recorded", "boolean", default=False)
    cr.execute(
        """
    WITH subcontracted_mo AS (
        SELECT DISTINCT mp.id
          FROM mrp_production mp
          JOIN stock_move sm1 ON (sm1.production_id = mp.id AND sm1.product_id = mp.product_id)
          JOIN stock_move_move_rel sm_rel ON sm_rel.move_orig_id = sm1.id
          JOIN stock_move sm2 ON sm2.id = sm_rel.move_dest_id
          JOIN stock_move_line sml ON sml.move_id = sm2.id
         WHERE sm2.is_subcontract = TRUE AND sml.qty_done > 0
    )
    UPDATE mrp_production mp
       SET subcontracting_has_been_recorded = TRUE
      FROM subcontracted_mo sub_mo
     WHERE mp.id = sub_mo.id
        """
    )

    util.create_column(cr, "stock_warehouse", "subcontracting_resupply_type_id", "int4")
    cr.execute(
        """
        UPDATE stock_warehouse
           SET subcontracting_resupply_type_id = out_type_id
         WHERE subcontracting_to_resupply = True
        """
    )
