# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "delivery_carrier", "return_label_on_delivery", "boolean")
    util.create_column(cr, "delivery_carrier", "get_return_label_from_portal", "boolean")
    util.remove_field(cr, "sale.order", "invoice_shipping_on_delivery")
    util.remove_field(cr, "choose.delivery.package", "stock_quant_package_id")
    util.create_column(cr, "choose_delivery_package", "picking_id", "int4")
