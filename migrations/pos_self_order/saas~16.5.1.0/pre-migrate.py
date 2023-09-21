# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "pos_self_order.first_letter_of_odoo_logo_svg")
    util.remove_view(cr, "pos_self_order.qr_code")
    util.rename_xmlid(cr, "pos_self_order.index", "pos_self_order.mobile_index")

    util.remove_column(cr, "res_config_settings", "pos_self_order_view_mode")
    util.remove_column(cr, "res_config_settings", "pos_self_order_table_mode")
    util.remove_column(cr, "res_config_settings", "pos_self_order_pay_after")
    util.remove_column(cr, "res_config_settings", "pos_self_order_image")
    util.remove_column(cr, "res_config_settings", "pos_self_order_image_name")

    util.remove_field(cr, "pos.order.line", "selected_attributes")
    util.create_column(cr, "pos_config", "self_ordering_mode", "varchar", default="nothing")
    if util.column_exists(cr, "pos_config", "self_order_table_mode"):
        cr.execute(
            """
                UPDATE pos_config
                    SET self_ordering_mode = CASE
                        WHEN self_order_table_mode = TRUE THEN 'mobile'
                        WHEN self_order_view_mode = TRUE THEN 'consultation'
                        ELSE 'nothing'
                    END;"""
        )

    util.remove_field(cr, "pos.config", "self_order_image")
    util.remove_field(cr, "pos.config", "self_order_table_mode")
    util.remove_field(cr, "pos.config", "self_order_view_mode")
    util.remove_field(cr, "pos.config", "self_order_image_name")

    util.remove_field(cr, "res.config.settings", "pos_self_order_image")
    util.remove_field(cr, "res.config.settings", "pos_self_order_table_mode")
    util.remove_field(cr, "res.config.settings", "pos_self_order_view_mode")
    util.remove_field(cr, "res.config.settings", "pos_self_order_image_name")

    util.rename_field(cr, "pos.config", "self_order_pay_after", "self_ordering_pay_after")
    util.rename_field(cr, "res.config.settings", "pos_self_order_pay_after", "pos_self_ordering_pay_after")
    util.remove_view(cr, "pos_self_order.mobile_index")
