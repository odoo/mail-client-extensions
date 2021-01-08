# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    cr.execute(
        """
        CREATE TABLE mrp_production_schedule(
            id SERIAL PRIMARY KEY,
            create_uid integer,
            create_date timestamp without time zone,
            write_uid integer,
            write_date timestamp without time zone,
            company_id integer,
            product_id integer NOT NULL,
            sequence integer,
            warehouse_id integer, -- NOT NULL, -- should be required, but sale_forecast.warehouse_id wasn't, forbidding migration
            forecast_target_qty float8,
            min_to_replenish_qty float8,
            max_to_replenish_qty float8
        )
    """
    )
    cr.execute(
        """
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
    """
    )

    cr.execute(
        """
        WITH default_warehouses AS (
            SELECT company_id, min(id) as id
              FROM stock_warehouse
          GROUP BY company_id
        )
        INSERT INTO mrp_production_schedule(product_id, company_id, sequence, warehouse_id,
                                            forecast_target_qty, min_to_replenish_qty, max_to_replenish_qty)
             SELECT p.id, COALESCE(t.company_id, u.company_id), t.sequence, COALESCE(f.warehouse_id, w.id),
                    p.mps_forecasted, p.mps_min_supply, p.mps_max_supply
               FROM sale_forecast f
               JOIN product_product p ON p.id = f.product_id
               JOIN product_template t ON t.id = p.product_tmpl_id
          LEFT JOIN res_users u ON u.id = COALESCE(f.create_uid, f.write_uid)
          LEFT JOIN default_warehouses w ON w.company_id = COALESCE(t.company_id, u.company_id)
           GROUP BY p.id, COALESCE(t.company_id, u.company_id), t.sequence, COALESCE(f.warehouse_id, w.id),
                    p.mps_forecasted, p.mps_min_supply, p.mps_max_supply
    """
    )

    cr.execute(
        """
        INSERT INTO mrp_product_forecast(production_schedule_id, "date", forecast_qty,
                                         replenish_qty, replenish_qty_updated, procurement_launched)

             SELECT s.id, f."date", f.forecast_qty,
                    f.to_supply, (f.mode = 'manual'), (f.state = 'done')
               FROM sale_forecast f
               JOIN mrp_production_schedule s ON s.product_id = f.product_id AND s.warehouse_id = f.warehouse_id
    """
    )

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

    # demo data ¯\_(ツ)_/¯
    cr.execute(
        """
        INSERT INTO ir_model_data(module,name,model,res_id,noupdate)
             SELECT 'mrp_mps', 'mrp_mps_production_schedule_1', 'mrp.production.schedule', id, true
               FROM mrp_production_schedule
              WHERE warehouse_id = %(warehouse)s
                AND product_id = %(product_12)s
              UNION
             SELECT 'mrp_mps', 'mrp_mps_production_schedule_2', 'mrp.production.schedule', id, true
               FROM mrp_production_schedule
              WHERE warehouse_id = %(warehouse)s
                AND product_id = %(product_3)s
              UNION
             SELECT 'mrp_mps', 'mrp_mps_production_schedule_3', 'mrp.production.schedule', id, true
               FROM mrp_production_schedule
              WHERE warehouse_id = %(warehouse)s
                AND product_id = %(product_13)s
              UNION
             SELECT 'mrp_mps', 'mrp_mps_production_schedule_5', 'mrp.production.schedule', id, true
               FROM mrp_production_schedule
              WHERE warehouse_id = %(warehouse)s
                AND product_id = %(product_16)s
        RETURNING id
        """,
        {
            "warehouse": util.ref(cr, "stock.warehouse0"),
            "product_12": util.ref(cr, "product.product_product_12"),
            "product_3": util.ref(cr, "product.product_product_3"),
            "product_13": util.ref(cr, "product.product_product_13"),
            "product_16": util.ref(cr, "product.product_product_16"),
        },
    )
