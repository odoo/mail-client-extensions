# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_constraint(cr, "stock_production_lot", "stock_production_lot_name_ref_uniq")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("stock.access_stock_location_{_,}partner_manager"))

    gone_access = """
        picking_portal
        picking_type
        move_portal
        location_stock_manager
        wharehouse_orderpoint_portal
        rule_manager
        move_line_portal
    """
    for xid in util.splitlines(gone_access):
        util.remove_record(cr, f"stock.access_stock_{xid}")

    # removed actions
    util.remove_record(cr, "stock.act_product_stock_move_open")
    util.remove_record(cr, "stock.action_receipt_picking_move")
    util.remove_record(cr, "stock.product_template_open_quants")
