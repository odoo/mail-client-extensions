# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # https://github.com/odoo/odoo/pull/78631
    util.create_column(cr, "repair_line", "price_total", "numeric")
    util.create_column(cr, "repair_fee", "price_total", "numeric")
