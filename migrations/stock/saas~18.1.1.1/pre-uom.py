from psycopg2 import sql

from odoo.addons.stock.models.product import UomUom

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "product.replenish", "product_uom_category_id")
    util.remove_field(cr, "stock.move", "product_packaging_id")
    util.remove_field(cr, "stock.move", "product_packaging_quantity")
    util.remove_field(cr, "stock.move", "product_packaging_qty")
    util.remove_field(cr, "stock.move", "product_uom_category_id")
    util.remove_field(cr, "stock.move.line", "product_packaging_qty")
    util.remove_field(cr, "stock.move.line", "product_uom_category_id")
    util.rename_field(cr, "stock.route", "packaging_selectable", "package_type_selectable")
    util.remove_field(cr, "stock.route", "packaging_ids")
    util.remove_field(cr, "stock.scrap", "product_uom_category_id")
    util.remove_field(cr, "stock.warehouse.orderpoint", "qty_multiple")
    util.remove_view(cr, "stock.label_product_packaging_view")

    util.create_column(cr, "stock_move", "packaging_uom_id", "int4")
    util.create_column(cr, "stock_move", "packaging_uom_qty", "float8")
    data = [
        # `product_uom` is renamed to `product_uom_id` in sale/saas~18.1.1.2/pre-migrate.py and purchase/saas~18.1.1.2/pre-migrate.py
        (
            module,
            join_column,
            table,
            "product_uom_id" if util.column_exists(cr, table, "product_uom_id") else "product_uom",
            qty_column,
        )
        for module, join_column, table, qty_column in [
            ("sale_stock", "sale_line_id", "sale_order_line", "product_uom_qty"),
            ("purchase_stock", "purchase_line_id", "purchase_order_line", "product_qty"),
            ("mrp", "production_id", "mrp_production", "product_qty"),
        ]
        if util.module_installed(cr, module) and util.column_exists(cr, "stock_move", join_column)
    ]
    packaging_cases = sql.SQL(
        "\n".join(
            f"WHEN sm.{join_column} IS NOT NULL THEN {table}.{uom_column}"
            for _, join_column, table, uom_column, _ in data
        )
    )
    qty_cases = sql.SQL(
        "\n".join(
            f"WHEN sm.{join_column} IS NOT NULL THEN {table}.{qty_column}"
            for _, join_column, table, _, qty_column in data
        )
    )
    left_joins = sql.SQL(
        "\n".join(f"LEFT JOIN {table} ON {join_column} = {table}.id" for _, join_column, table, _, _ in data)
    )
    util.explode_execute(
        cr,
        util.format_query(
            cr,
            """
            WITH cte_m2m_orig_dest AS (
                SELECT sm.id AS stock_move_id,
                    MIN(CASE WHEN rel.move_dest_id = sm.id THEN sm_orig.product_uom END) AS orig_product_uom,
                    MIN(CASE WHEN rel.move_orig_id = sm.id THEN sm_dest.product_uom END) AS dest_product_uom,
                    MIN(CASE WHEN rel.move_dest_id = sm.id THEN sm_orig.product_uom_qty END) AS orig_product_uom_qty,
                    MIN(CASE WHEN rel.move_orig_id = sm.id THEN sm_dest.product_uom_qty END) AS dest_product_uom_qty
                FROM stock_move sm
            LEFT JOIN stock_move_move_rel rel ON sm.id IN (rel.move_dest_id, rel.move_orig_id)
            LEFT JOIN stock_move sm_orig ON rel.move_orig_id = sm_orig.id
            LEFT JOIN stock_move sm_dest ON rel.move_dest_id = sm_dest.id
                WHERE {{parallel_filter}}
            GROUP BY sm.id
            ),
            cte_move_relations AS (
                SELECT sm.id AS stock_move_id,
                    CASE
                        {packaging_cases}
                        WHEN cte_m2m_orig_dest.orig_product_uom IS NOT NULL THEN cte_m2m_orig_dest.orig_product_uom
                        WHEN cte_m2m_orig_dest.dest_product_uom IS NOT NULL THEN cte_m2m_orig_dest.dest_product_uom
                        ELSE sm.product_uom
                    END AS new_packaging_uom_id,
                    CASE
                        {qty_cases}
                        WHEN cte_m2m_orig_dest.orig_product_uom_qty IS NOT NULL THEN cte_m2m_orig_dest.orig_product_uom_qty
                        WHEN cte_m2m_orig_dest.dest_product_uom_qty IS NOT NULL THEN cte_m2m_orig_dest.dest_product_uom_qty
                        ELSE sm.product_uom_qty
                    END AS new_packaging_uom_qty
                  FROM cte_m2m_orig_dest
                  JOIN stock_move sm
                    ON sm.id = cte_m2m_orig_dest.stock_move_id
                  {left_joins}
            )
            UPDATE stock_move sm
            SET packaging_uom_id = cte.new_packaging_uom_id,
                packaging_uom_qty = cte.new_packaging_uom_qty
            FROM cte_move_relations cte
            WHERE sm.id = cte.stock_move_id
            """,
            packaging_cases=packaging_cases,
            qty_cases=qty_cases,
            left_joins=left_joins,
        ),
        table="stock_move",
        alias="sm",
    )


class Uom(UomUom):
    _name = "uom.uom"
    _inherit = "uom.uom"
    _module = "stock"

    def write(self, vals):
        # /uom/saas~18.1.1.0/end-migrate.py makes the hour the relative uom
        if self.env.context.get("_upg_swap_time_uom_ref"):
            return super(UomUom, self).write(vals)
        return super().write(vals)
