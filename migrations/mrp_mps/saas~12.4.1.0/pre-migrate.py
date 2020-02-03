# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    cr.execute("""
        CREATE TABLE mrp_production_schedule(
            id SERIAL PRIMARY KEY,
            create_uid integer,
            create_date timestamp without time zone,
            write_uid integer,
            write_date timestamp without time zone,
            company_id integer,
            product_id integer NOT NULL,
            sequence integer,
            warehouse_id integer, -- NOT NULL,     -- should be required, but sale_forecast.warehouse_id wasn't, forbidding migration
            forecast_target_qty float8,
            min_to_replenish_qty float8,
            max_to_replenish_qty float8
        )
    """)
    cr.execute("""
        CREATE TABLE mrp_product_forecast(
            id SERIAL PRIMARY KEY,
            create_uid integer,
            create_date timestamp without time zone,
            write_uid integer,
            write_date timestamp without time zone,
            production_schedule_id integer NOT NULL,
            "date" date,
            forecast_qty float8,
            replenish_qty float8,
            replenish_qty_updated boolean,
            procurement_launched boolean
        )
    """)

    cr.execute("""
        INSERT INTO mrp_production_schedule(product_id, company_id, sequence, warehouse_id,
                                            forecast_target_qty, min_to_replenish_qty, max_to_replenish_qty)
             SELECT p.id, t.company_id, t.sequence, f.warehouse_id,
                    p.mps_forecasted, p.mps_min_supply, p.mps_max_supply
               FROM sale_forecast f
               JOIN product_product p ON p.id = f.product_id
               JOIN product_template t ON t.id = p.product_tmpl_id
           GROUP BY p.id, t.company_id, t.sequence, f.warehouse_id,
                    p.mps_forecasted, p.mps_min_supply, p.mps_max_supply
    """)

    cr.execute("""
        INSERT INTO mrp_product_forecast(production_schedule_id, "date", forecast_qty,
                                         replenish_qty, replenish_qty_updated, procurement_launched)

             SELECT s.id, f."date", f.forecast_qty,
                    f.to_supply, (f.mode = 'manual'), (f.state = 'done')
               FROM sale_forecast f
               JOIN mrp_production_schedule s ON s.product_id = f.product_id AND s.warehouse_id = f.warehouse_id
    """)

    # remove old stuff
    util.remove_model(cr, "sale.forecast")
    util.remove_model(cr, "sale.forecast.indirect")
    util.remove_model(cr, "mrp.mps.report")

    for f in {"active", "forecasted", "min_supply", "max_supply", "apply"}:
        util.remove_field(cr, "product.product", "mps_" + f)

    util.remove_field(cr, "product.product", "apply_active")

    util.remove_view(cr, "mrp_mps.report_inventory")
    util.remove_view(cr, "mrp_mps.product_product_view_form_mps")
    util.remove_record(cr, "mrp_mps.mrp_mps_report_action_client")
    util.remove_record(cr, "mrp_mps.mrp_mps_menu_planning")
    util.remove_record(cr, "mrp_mps.mpr_mps_report_menu")
