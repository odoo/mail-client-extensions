# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    mods = "purchase_requisition{,_stock}"

    util.move_field_to_module(cr, "purchase.requisition", "warehouse_id", *eb(mods))
    util.move_field_to_module(cr, "purchase.requisition", "picking_type_idg", *eb(mods))
    util.move_field_to_module(cr, "purchase.requisition.line", "move_dest_id", *eb(mods))
    util.move_field_to_module(cr, "stock.move", "requisition_line_ids", *eb(mods))

    # field was defined twice, remove the one with the typo
    util.update_field_usage(cr, "stock.move", *eb("requis{,i}tion_line_ids"))
    util.remove_field(cr, "stock.move", "requistion_line_ids")

    util.rename_xmlid(cr, *eb(mods + ".access_purchase_requisition_stock_manager"))
    util.rename_xmlid(cr, *eb(mods + ".access_purchase_requisition_line_stock_manager"))
