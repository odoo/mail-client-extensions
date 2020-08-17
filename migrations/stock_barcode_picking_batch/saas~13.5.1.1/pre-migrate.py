# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    util.create_column(cr, "stock_quant_package", "package_use", "varchar", default="disposable")
