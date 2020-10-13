# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "pos_config", "set_tip_after_payment", "boolean", default=False)
    util.create_column(cr, "restaurant_floor", "active", "boolean", default=True)
