from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "repair.view_repair_warn_uncomplete_move")
    util.remove_model(cr, "repair.warn.uncomplete.move")

    util.create_column(cr, "stock_warehouse", "repair_mto_pull_id", "int4")

    mto_route = util.ref(cr, "stock.route_warehouse0_mto")
    if mto_route:
        cr.execute(
            """
        WITH inserted_rules AS (
          INSERT INTO stock_rule (
                      name,
                      procure_method, company_id, action, auto, route_id,
                      location_dest_id, location_src_id, picking_type_id, active
                  )
               SELECT jsonb_build_object('en_US', sw.code || ': ' || src_loc.name::text || ' → ' || dest_loc.name::text || ' (MTO)'),
                      'mts_else_mto', sw.company_id, 'pull', 'manual', %s,
                      spt.default_location_dest_id, spt.default_location_src_id, spt.id, True
                 FROM stock_warehouse sw
                 JOIN stock_location dest_loc
                   ON dest_loc.company_id = sw.company_id
                 JOIN stock_location src_loc
                   ON src_loc.id = sw.lot_stock_id
                 JOIN stock_picking_type spt
                   ON spt.warehouse_id = sw.id
                WHERE dest_loc.usage = 'production'
                  AND spt.code = 'repair_operation'
            RETURNING id, company_id
        )
        UPDATE stock_warehouse sw
           SET repair_mto_pull_id = ir.id
          FROM inserted_rules ir
         WHERE sw.company_id = ir.company_id
        """,
            (mto_route,),
        )
