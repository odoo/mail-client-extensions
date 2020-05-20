# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "product.template", "rental")

    # Now required
    cr.execute("UPDATE product_pricelist SET discount_policy='with_discount' WHERE discount_policy IS NULL")
