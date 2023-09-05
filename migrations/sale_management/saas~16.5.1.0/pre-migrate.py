# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_order_template", "prepayment_percent", "numeric", default=1.0)
