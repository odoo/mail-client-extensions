# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # https://github.com/odoo/odoo/commit/489e76ade600f7983a9a1976c04529ac542fdd44
    # This field was added in saas~14.3 but got to be a stored computed on 15.0
    util.create_column(cr, "stock_quant", "inventory_quantity_set", "bool")
