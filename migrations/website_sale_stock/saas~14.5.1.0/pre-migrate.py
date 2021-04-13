# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_config_settings", "allow_out_of_stock_order", "boolean", default=True)
    util.create_column(cr, "res_config_settings", "show_availability", "boolean", default=False)
    util.create_column(cr, "product_template", "allow_out_of_stock_order", "boolean", default=True)
    util.create_column(cr, "product_template", "show_availability", "boolean", default=False)
    util.rename_field(cr, "product.template", "custom_message", "out_of_stock_message")
    util.convert_field_to_html(cr, "product.template", "out_of_stock_message")

    cr.execute(
        """
        UPDATE product_template
           SET allow_out_of_stock_order = False,
               show_availability = True
         WHERE inventory_availability != 'never'
    """
    )

    cr.execute(
        """
        UPDATE product_template
           SET available_threshold = 0
         WHERE inventory_availability not in ('always', 'threshold')
    """
    )
