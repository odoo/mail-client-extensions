# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "purchase_order", "picking_count")
    util.rename_field(cr, "purchase.order", "picking_count", "incoming_picking_count")
