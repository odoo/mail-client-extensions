# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # https://github.com/odoo/odoo/pull/85157
    util.create_column(cr, "stock_picking_type", "is_repairable", "boolean")
