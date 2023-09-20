# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_order_template", "prepayment_percent", "numeric", default=1.0)
    util.remove_field(cr, "res.config.settings", "module_sale_quotation_builder")
