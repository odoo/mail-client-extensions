# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    xids = util.splitlines(
        """
        route_warehouse0_buy
        exception_on_po

        stock_move_purchase
        view_warehouse_inherited
        purchase_open_picking
        menu_action_picking_tree_in_move

        res_config_settings_view_form_stock

        access_purchase_order_stock_worker
        access_purchase_order_line_stock_worker

        access_stock_location_purchase_user
        access_stock_warehouse_purchase_user
        access_stock_picking_purchase_user
        access_stock_move_purchase_user

        access_stock_location_purchase_user_manager
        access_stock_warehouse_purchase_user_manager
        access_stock_picking_purchase_user_manager
        access_stock_move_purchase_user_manager

        access_stock_location_purchase_manager
        access_stock_warehouse_orderpoint_user
        access_stock_warehouse_orderpoint_manager
    """
    )
    for x in xids:
        util.rename_xmlid(cr, "purchase." + x, "purchase_stock." + x)

    moved_fields = {
        "purchase.order": {
            "picking_count",
            "picking_ids",
            "incoterm_id",
            "picking_type_id",
            "default_location_dest_id_usage",
            "group_id",
            "is_shipped",
        },
        "purchase.order.line": {"move_ids", "orderpoint_ids", "move_dest_ids"},
        "res.config.settings": {"module_stock_dropshipping", "is_installed_sale"},
        "purchase.report": {"picking_type_id"},
        "stock.picking": {"purchase_id"},
        "stock.move": {"created_purchase_line_id", "purchase_line_id"},
        "stock.warehouse": {"buy_to_resupply", "buy_pull_id"},
    }

    for model, fields in moved_fields.items():
        for field in fields:
            util.move_field_to_module(cr, model, field, "purchase", "purchase_stock")
