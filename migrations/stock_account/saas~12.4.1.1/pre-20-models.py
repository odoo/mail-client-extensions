# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Move stock_move data into layers table
    cr.execute("""
        CREATE TABLE stock_valuation_layer(
            id SERIAL PRIMARY KEY,
            create_uid integer,
            create_date timestamp without time zone,
            write_uid integer,
            write_date timestamp without time zone,
            company_id integer,
            product_id integer,
            quantity numeric,
            unit_cost numeric,
            value numeric,
            remaining_qty numeric,
            description varchar,
            stock_valuation_layer_id integer,
            stock_move_id integer,
            account_move_id integer
        )
    """)

    # Product in manual valuation
    cr.execute("""
        INSERT INTO stock_valuation_layer(
            create_uid,
            create_date,
            write_uid,
            write_date,
            company_id,
            product_id,
            quantity,
            unit_cost,
            value,
            remaining_qty,
            description,
            stock_move_id
        )
        SELECT
            sm.create_uid,
            sm.create_date,
            sm.write_uid,
            sm.write_date,
            sm.company_id,
            pp.id,
            CASE
                WHEN (ls.usage = 'internal' OR ls.usage = 'transit' AND ls.company_id IS NOT NULL) AND ld.usage != 'internal' THEN -sm.product_qty
                WHEN ls.usage != 'internal' AND (ld.usage = 'internal' OR ld.usage = 'transit' AND ld.company_id IS NOT NULL) THEN sm.product_qty
            END as quantity,
            sm.price_unit,
            sm.value,
            sm.remaining_qty,
            sm.reference,
            sm.id
        FROM stock_move sm
        LEFT JOIN stock_location ls ON (ls.id = sm.location_id)
        LEFT JOIN stock_location ld ON (ld.id = sm.location_dest_id)
        LEFT JOIN product_product pp ON pp.id = sm.product_id
        LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
        LEFT JOIN product_category pc ON pc.id = pt.categ_id
        WHERE
            sm.state = 'done' AND
            sm.value != 0 AND
            'product.category,' || pc.id NOT IN
                (SELECT res_id FROM ir_property
                WHERE
                    name = 'property_valuation' AND
                    value_text = 'real_time' AND
                    company_id = sm.company_id)
    """)

    # Product in automated valuation
    cr.execute("""
        INSERT INTO stock_valuation_layer(
            create_uid,
            create_date,
            write_uid,
            write_date,
            company_id,
            product_id,
            quantity,
            value,
            unit_cost,
            remaining_qty,
            description,
            stock_move_id,
            account_move_id
        )
        SELECT
            aml.create_uid,
            aml.create_date,
            aml.write_uid,
            aml.write_date,
            aml.company_id,
            aml.product_id,
            aml.quantity,
            aml.debit - aml.credit,
            sm.price_unit,
            sm.remaining_qty,
            aml.ref,
            am.stock_move_id,
            aml.move_id
        FROM account_move_line aml
        LEFT JOIN account_move am ON am.id = aml.move_id
        INNER JOIN stock_move sm ON am.stock_move_id = sm.id
        LEFT JOIN product_product pp ON pp.id = aml.product_id
        LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
        LEFT JOIN product_category pc ON pc.id = pt.categ_id
        WHERE
            'account.account,' || aml.account_id IN
                (SELECT value_reference FROM ir_property
                WHERE
                    name = 'property_stock_valuation_account_id' AND
                    (res_id IS NULL OR res_id = 'product.category,' || pt.categ_id) AND
                    company_id = aml.company_id ORDER by res_id LIMIT 1) AND
            'product.category,' || pc.id IN
                (SELECT res_id FROM ir_property
                WHERE
                    name = 'property_valuation' AND
                    value_text = 'real_time' AND
                    company_id = aml.company_id)
    """)

    util.remove_field(cr, "product.product", "stock_value_currency_id")
    util.remove_field(cr, "product.product", "stock_value")
    util.remove_field(cr, "product.product", "qty_at_date")
    util.remove_field(cr, "product.product", "stock_fifo_real_time_aml_ids")
    util.remove_field(cr, "product.product", "stock_fifo_manual_move_ids")

    util.remove_field(cr, "stock.move", "value")
    util.remove_field(cr, "stock.move", "remaining_qty")

    util.remove_record(cr, "stock_account.product_valuation_action")
    util.remove_view(cr, "stock_account.view_stock_product_tree2")
    util.remove_view(cr, "stock_account.view_stock_account_aml")
    util.remove_view(cr, "stock_account.view_move_tree_valuation_at_date")

    util.create_column(cr, "stock_return_picking_line", "to_refund", "boolean")
