# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "project.project", "purchase_order_count", "purchase_orders_count")
