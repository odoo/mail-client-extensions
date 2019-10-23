# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.move_field_to_module(cr, "res.company", "padding_time", "sale_renting", "sale_stock_renting")
    util.move_field_to_module(cr, "res.config.settings", "padding_time", "sale_renting", "sale_stock_renting")

    util.create_column(cr, "rental_wizard", "uom_id", "int4")
    util.create_column(cr, "rental_wizard", "pricelist_id", "int4")
    util.create_column(cr, "rental_wizard", "pricing_explanation", "text")
    util.create_column(cr, "rental_pricing", "pricelist_id", "int4")

    cr.execute("ALTER TABLE rental_pricing ALTER COLUMN duration TYPE int4")

    util.rename_field(cr, "res.config.settings", "module_sale_rental_sign", "module_sale_renting_sign")
    util.rename_field(cr, "sale.order.line", "qty_picked_up", "qty_returned")
    util.rename_field(cr, "rental.processing.line", "qty_picked_up", "qty_returned")

    util.remove_field(cr, "product.template", "preparation_time")

    util.remove_model(cr, "sale.rental.report")
    util.remove_model(cr, "sale.rental.schedule")
