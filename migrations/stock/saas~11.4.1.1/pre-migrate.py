# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "stock.move.line", "in_entire_package", "picking_type_entire_packs")

    util.remove_field(cr, "stock.picking", "entire_package_ids")
    util.remove_field(cr, "stock.picking", "entire_package_detail_ids")

    for field in {
        "move_line_ids",
        "current_picking_move_line_ids",
        "current_picking_id",
        "current_source_location_id",
        "current_destination_location_id",
        "is_processed",
    }:
        util.remove_field(cr, "stock.quant.package", field)

    util.remove_view(cr, "stock.view_quant_package_picking_tree")
