# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # The column needs to be populated before Odoo sets the NOT NULL restriction, or it will fire:
    # > unable to set NOT NULL on column 'stock_notification'
    util.create_column(cr, "product_wishlist", "stock_notification", "bool", default=False)
