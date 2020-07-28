# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    util.recompute_fields(cr, "stock.warehouse.orderpoint", ["qty_to_order"])
    env["stock.warehouse"]._check_multiwarehouse_group()
