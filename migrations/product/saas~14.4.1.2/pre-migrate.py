# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # new constraint add to only allow qty to be positive
    # for records with non-positive qty, we change it to 1.0
    cr.execute("UPDATE product_packaging SET qty = 1.0 WHERE COALESCE(qty, 0) <= 0")

    # convert text data to html data
    util.convert_field_to_html(cr, "product.template", "description")
