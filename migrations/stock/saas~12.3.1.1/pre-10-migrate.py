# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "stock_picking", "user_id", "int4")
    util.create_column(cr, "stock_production_lot", "note", "text")
