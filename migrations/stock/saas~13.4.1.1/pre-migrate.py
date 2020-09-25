# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    util.remove_field(cr, "res.config.settings", "group_stock_multi_warehouses")

    util.create_column(cr, "stock_warehouse_orderpoint", "trigger", "varchar", default="auto")
    util.create_column(cr, "stock_warehouse_orderpoint", "snoozed_until", "date")
    util.create_column(cr, "stock_warehouse_orderpoint", "product_category_id", "int4")
    util.create_column(cr, "stock_warehouse_orderpoint", "route_id", "int4")
    util.create_column(cr, "stock_warehouse_orderpoint", "qty_to_order", "float8")  # computed in end-
    cr.execute(
        """
            UPDATE stock_warehouse_orderpoint o
               SET product_category_id = t.categ_id
              FROM product_product p
              JOIN product_template t ON t.id = p.product_tmpl_id
             WHERE p.id = o.product_id
        """
    )

    util.rename_xmlid(cr, *eb("stock.action_orderpoint{_form,}"))
    util.remove_record(cr, "stock.access_ir_property_group_stock_manager")
    util.remove_record(cr, "stock.product_open_orderpoint")

    util.remove_view(cr, "stock.stock_warehouse_view_form_editable")
    util.remove_view(cr, "stock.stock_warehouse_view_tree_editable")
    util.remove_view(cr, "stock.view_warehouse_orderpoint_tree")
