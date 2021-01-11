# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    line_map = {
        1: (4, 1),
        2: (4, 2),
        4: (11, 1),
    }
    for line, (product, attribute) in line_map.items():
        util.rename_xmlid(
            cr,
            f"product.product_template_attribute_line_{line}",
            f"product.product_{product}_attribute_{attribute}_product_template_attribute_line",
        )

    value_map = {
        1: 4,
        2: 11,
    }
    for value, product in value_map.items():
        util.rename_xmlid(
            cr,
            f"product.product_template_attribute_value_{value}",
            f"product.product_{product}_attribute_1_value_2",
        )

    sale_map = {
        3: (4, 1, 1),
        4: (11, 1, 1),
        5: (4, 2, 2),
    }

    for value_from, (product, attribute, value_to) in sale_map.items():
        util.rename_xmlid(
            cr,
            f"sale.product_template_attribute_value_{value_from}",
            f"product.product_{product}_attribute_{attribute}_value_{value_to}",
        )
