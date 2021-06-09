# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    """
    A new MTO stock rule has to be created for each warehouse company.
    New 'production' locations linked to compagnies must be created before (this is done in stock/saas~12.1.1.1/end-migrate.py).
    """
    try:
        mto_route = util.env(cr)["stock.warehouse"]._find_global_route("stock.route_warehouse0_mto", "Make To Order").id
    except Exception:
        mto_route = False

    if mto_route:
        cr.execute(
            """
            INSERT INTO stock_rule (
                        name,
                        procure_method,
                        company_id,
                        action,
                        auto,
                        route_id,
                        location_id,
                        location_src_id,
                        picking_type_id,
                        active
                   )
                   SELECT
                        CASE
                            WHEN sw.manufacture_steps = 'mrp_one_step' THEN sw.code || ': ' || stock_loc.name
                                                        || ' → ' || prod_loc.name || ' (MTO)'
                            ELSE sw.code || ': ' || pbm_loc.name || ' → ' || prod_loc.name || ' (MTO)'
                        END,
                        'make_to_order',
                        sw.company_id,
                        'pull',
                        'manual',
                        %s,
                        prod_loc.id,
                        CASE
                            WHEN sw.manufacture_steps = 'mrp_one_step' THEN sw.lot_stock_id
                            ELSE sw.pbm_loc_id
                        END,
                        spt.id,
                        true
              FROM stock_warehouse sw
              JOIN stock_location prod_loc ON prod_loc.company_id = sw.company_id AND prod_loc.usage = 'production'
              JOIN stock_location stock_loc ON stock_loc.id = sw.lot_stock_id
              JOIN stock_location pbm_loc ON pbm_loc.id = sw.pbm_loc_id
              JOIN stock_picking_type spt ON spt.warehouse_id = sw.id AND spt.code = 'mrp_operation'
            """,
            (mto_route,),
        )

    virtual_production_loc_id = util.ref(cr, "stock.location_production")
    cr.execute(
        """UPDATE stock_rule rule
           SET location_id=prod_loc.id,
               location_src_id = CASE
                     WHEN sw.manufacture_steps = 'mrp_one_step' THEN sw.lot_stock_id
                     ELSE sw.pbm_loc_id
                     END,
                     picking_type_id = spt.id
          FROM stock_warehouse sw
          JOIN stock_location prod_loc ON prod_loc.company_id = sw.company_id AND prod_loc.usage = 'production'
          JOIN stock_location stock_loc ON stock_loc.id = sw.lot_stock_id
          JOIN stock_location pbm_loc ON pbm_loc.id = sw.pbm_loc_id
          JOIN stock_picking_type spt ON spt.warehouse_id = sw.id AND spt.code = 'mrp_operation'
         WHERE rule.location_id = %s
           AND rule.company_id = sw.company_id
    """,
        [virtual_production_loc_id],
    )
