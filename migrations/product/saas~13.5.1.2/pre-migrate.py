# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    move_fields = {
        "product.attribute": [("display_type", "varchar", "radio")],
        "product.attribute.value": [
            ("is_custom", "boolean", False),
            ("html_color", "varchar", None),
            ("display_type", None, None),
        ],
        "product.template.attribute.value": [
            ("is_custom", None, None),
            ("html_color", None, None),
            ("display_type", None, None),
        ],
    }
    for model, fields in move_fields.items():
        for field, ftype, default in fields:
            util.move_field_to_module(cr, model, field, "sale", "product")
            if ftype is not None:
                table = util.table_of_model(cr, model)
                util.create_column(cr, table, field, ftype, default=default)

    util.move_model(cr, "product.attribute.custom.value", "sale", "product")
    # The field sale_order_line_id and constraint stay in sale module
    util.move_field_to_module(cr, "product.attribute.custom.value", "sale_order_line_id", "product", "sale")
    util.rename_xmlid(cr, *eb("{product,sale}.constraint_product_attribute_custom_value_sol_custom_value_unique"))
