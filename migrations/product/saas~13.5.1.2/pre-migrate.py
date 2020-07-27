# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    move_fields = {
        "product.attribute": ["display_type"],
        "product.attribute.value": ["is_custom", "html_color", "display_type"],
        "product.template.attribute.value": ["is_custom", "html_color", "display_type"],
        "product.attribute.custom.value": ["nale", "custom_product_template_attribute_value_id", "custom_value"],
    }
    for model, fields in move_fields.items():
        for field in fields:
            util.move_field_to_module(cr, model, field, "sale", "product")
