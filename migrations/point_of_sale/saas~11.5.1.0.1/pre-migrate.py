# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "pos.config", "module_account_invoicing", "module_account")
    util.create_column(cr, "pos_order", "amount_tax", "float8")
    util.create_column(cr, "pos_order", "amount_total", "float8")
    util.create_column(cr, "pos_order", "amount_paid", "float8")
    util.create_column(cr, "pos_order", "amount_return", "float8")
    util.create_column(cr, "pos_order_line", "price_subtotal", "float8")
    util.create_column(cr, "pos_order_line", "price_subtotal_incl", "float8")

    util.remove_field(cr, "pos.order.report", "stock_location_id")

    util.remove_model(cr, "pos.discount")
