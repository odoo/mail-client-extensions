# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    util.rename_field(cr, "stock.location", "pull_ids", "rule_ids")
    util.remove_field(cr, "stock.location", "push_ids")

    util.rename_model(cr, "procurement.rule", "stock.rule")
    util.create_column(cr, "stock_rule", "auto", "varchar")
    cr.execute("UPDATE stock_rule SET action='pull'")

    cr.execute(
        """
        INSERT INTO stock_rule (name, company_id, route_id, location_src_id, location_id, delay,
                                picking_type_id, auto, propagate, active, warehouse_id,
                                route_sequence, sequence, action)
             SELECT name, company_id, route_id, location_from_id, location_dest_id, delay,
                    picking_type_id, auto, propagate, active, warehouse_id,
                    route_sequence, sequence, 'push'
               FROM stock_location_path
    """
    )
    util.remove_model(cr, "stock.location.path")

    util.remove_field(cr, "stock.move", "ordered_qty")
    util.remove_field(cr, "stock.move", "push_rule_id")

    util.remove_field(cr, "stock.move.line", "ordered_qty")
    util.remove_field(cr, "stock.move.line", "from_loc")
    util.remove_field(cr, "stock.move.line", "to_loc")

    util.remove_field(cr, "stock.picking.type", "barcode_nomenclature_id")

    util.remove_field(cr, "stock.warehouse", "default_resupply_wh_id")

    util.rename_xmlid(cr, *eb("stock.report_lot_{barcode,label}"))
    util.rename_xmlid(cr, *eb("stock.action_report_lot_{barcode,label}"))

    util.rename_xmlid(cr, *eb("stock.access_{procurement,stock}_rule"))
    util.rename_xmlid(cr, *eb("stock.access_{procurement,stock}_rule_user"))
    util.rename_xmlid(cr, *eb("stock.access_{procurement,stock}_rule_manager"))
    util.rename_xmlid(cr, *eb("stock.access_{procurement,stock}_rule_stock_manager"))
    util.rename_xmlid(cr, *eb("stock.access_{procurement,stock}_rule_internal"))

    util.remove_field(cr, "stock.change.product.qty", "lot_id")
