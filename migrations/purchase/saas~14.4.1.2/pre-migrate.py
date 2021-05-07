# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "product_packaging", "purchase", "boolean", default=True)

    # convert text data to html data
    util.convert_field_to_html(cr, "purchase.order", "notes")
