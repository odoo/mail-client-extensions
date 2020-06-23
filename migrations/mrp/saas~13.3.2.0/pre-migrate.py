# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.move.line", "lot_produced_qty")

    util.remove_view(cr, "mrp.view_document_form")

    gone = """
        access_mrp_resource_manager

        act_product_mrp_production
        action_mrp_unbuild_move_line
        mrp_workcenter_productivity_loss_action
        mrp_workorder_delta_report
    """

    for xid in util.splitlines(gone):
        util.remove_record(cr, f"mrp.{xid}")
