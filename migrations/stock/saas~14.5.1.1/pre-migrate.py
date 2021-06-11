# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.warehouse.orderpoint", "json_lead_days_popover")
    util.remove_field(cr, "stock.warehouse.orderpoint", "allowed_route_ids")

    util.remove_field(cr, "stock.move", "has_move_lines")
    util.create_column(cr, "res_config_settings", "group_stock_reception_report", "boolean")
    util.create_column(cr, "res_config_settings", "group_stock_auto_reception_report", "boolean")

    util.remove_view(cr, "stock.label_product_template_view")
    util.remove_view(cr, "stock.label_barcode_product_template_view")
    util.remove_view(cr, "stock.label_barcode_product_product_view")
    util.remove_record(cr, "stock.label_product_template")
    util.remove_record(cr, "stock.label_barcode_product_template")
    util.remove_record(cr, "stock.label_barcode_product_product")
    util.remove_record(cr, "stock.action_label_transfer_template_zpl")
    util.remove_record(cr, "stock.action_label_transfer_template_pdf")
