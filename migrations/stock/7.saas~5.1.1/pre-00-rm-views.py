# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    """As deleted xmlid are deleted only at the end of the update, deleted
    views still exists in database during the update process and used when
    applying the view inheritance. If the views use a deleted field,
    this raise an error. We delete it ourself to avoid this.
    """
    for view in (
        "stock.view_picking_in_tree",
        "stock.view_picking_in_form",
        "stock.view_picking_in_search",
        "stock.view_picking_out_tree",
        "stock.view_picking_out_form",
        "stock.view_picking_out_search",
        "stock.view_normal_procurement_locations_form",
        "stock.view_normal_property_acc_form",
        "stock.view_category_property_form",
    ):
        util.remove_view(cr, view)
