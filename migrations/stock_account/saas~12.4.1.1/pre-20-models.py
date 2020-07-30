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

    util.remove_field(cr, "product.product", "stock_value_currency_id")
    util.remove_field(cr, "product.product", "stock_value")
    util.remove_field(cr, "product.product", "qty_at_date")
    util.remove_field(cr, "product.product", "stock_fifo_real_time_aml_ids")
    util.remove_field(cr, "product.product", "stock_fifo_manual_move_ids")

    util.remove_record(cr, "stock_account.product_valuation_action")
    util.remove_view(cr, "stock_account.view_stock_product_tree2")
    util.remove_view(cr, "stock_account.view_stock_account_aml")
    util.remove_view(cr, "stock_account.view_move_tree_valuation_at_date")

    util.create_column(cr, "stock_return_picking_line", "to_refund", "boolean")
