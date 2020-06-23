# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "purchase_order_line", "delay_alert", "boolean")
    util.create_column(cr, "res_company", "days_to_purchase", "float8")
