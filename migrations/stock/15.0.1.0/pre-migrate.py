# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # https://github.com/odoo/odoo/commit/489e76ade600f7983a9a1976c04529ac542fdd44
    # This field was added in saas~14.3 but got to be a stored computed on 15.0
    util.create_column(cr, "stock_quant", "inventory_quantity_set", "bool")

    # https://github.com/odoo/odoo/commit/0cf5c4e8241c46724defc0ea7e0d2c881ec2eeab
    util.drop_depending_views(cr, "stock_quant", "quantity")
    # converting float8 to numeric has some quirks, see commit introducing the change below
    cr.execute("ALTER TABLE stock_quant ALTER COLUMN quantity TYPE numeric USING quantity::text::numeric")
