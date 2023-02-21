# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    models_to_move = (
        "choose.delivery.package",
        "product.template",
        "stock.package.type",
        "stock.picking",
        "stock.quant.package",
        "stock.move.line",
        "stock.move",
    )
    for model in models_to_move:
        util.move_model(cr, model, "delivery", "stock_delivery", move_data=True)

    # rename moved demo data
    eb = util.expand_braces
    for suffix in {"confirmed", "assigned", "done"}:
        util.rename_xmlid(cr, *eb(f"stock_delivery.outgoing_shipment_with_carrier_{suffix}{{_1,}}"))

    util.move_field_to_module(cr, "sale.order", "shipping_weight", "delivery", "stock_delivery")

    views_to_move = (
        "choose_delivery_package_view_form",
        "delivery_stock_report_delivery_no_package_section_line",
        "delivery_tracking_url_warning_form",
        "label_package_template_view_delivery",
        "menu_action_delivery_carrier_form",
        "menu_delivery_zip_prefix",
        "product_template_hs_code",
        "report_delivery_document2",
        "report_package_barcode_delivery",
        "report_package_barcode_small_delivery",
        "report_shipping2",
        "stock_move_line_view_search_delivery",
        "stock_package_type_form_delivery",
        "stock_package_type_tree_delivery",
        "stock_report_delivery_aggregated_move_lines_inherit_delivery",
        "stock_report_delivery_has_serial_move_line_inherit_delivery",
        "stock_report_delivery_package_section_line_inherit_delivery",
        "view_move_line_tree_detailed_delivery",
        "view_picking_type_form_delivery",
        "view_picking_withcarrier_out_form",
        "view_picking_withweight_internal_move_form",
        "view_quant_package_weight_form",
        "view_stock_rule_form_delivery",
        "vpicktree_view_tree",
        # access rights
        "access_delivery_carrier_stock_user",
        "access_delivery_carrier_stock_manager",
        "access_delivery_zip_prefix_stock_manager",
        "access_delivery_price_rule_stock_manager",
        "access_choose_delivery_package",
        "access_choose_delivery_carrier",  # also renamed after move
    )
    for view in views_to_move:
        util.rename_xmlid(cr, f"delivery.{view}", f"stock_delivery.{view}")

    util.rename_xmlid(cr, *eb("stock_delivery.access_choose_delivery_carrier{,_stock_user}"))
    util.rename_xmlid(
        cr,
        "delivery.sale_order_portal_content_inherit_sale_stock_inherit_website_sale_delivery",
        "stock_delivery.sale_order_portal_content_inherit_sale_stock_inherit_website_sale",
    )
