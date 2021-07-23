# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.ENVIRON["no_model_data_delete"].update(
        {
            "product.category": "always",
            "product.product": "always",
            "product.template": "always",
            "product.pricelist": "always",
            "product.attribute": "always",
            "product.attribute.value": "always",
        }
    )
