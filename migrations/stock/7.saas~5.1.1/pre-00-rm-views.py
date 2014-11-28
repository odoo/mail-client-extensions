# -*- coding: utf-8 -*-
from operator import methodcaller
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """As deleted xmlid are deleted only at the end of the update, deleted
       views still exists in database during the update process and used when
       applying the view inheritance. If the views use a deleted field,
       this raise an error. We delete it ourself to avoid this.
    """

    views = filter(None, map(methodcaller('strip'), """
            sale_journal.sale_journal_picking_order_tree_in
        stock.view_picking_in_tree

            sale_journal.sale_journal_picking_order_in
        stock.view_picking_in_form

            claim_from_delivery.crm_claim_from_delivery
            sale_stock.stock_picking_out_inherit_sale
            sale_journal.sale_journal_picking_order_tree_out
        stock.view_picking_out_tree

            sale_journal.sale_journal_picking_order_out
        stock.view_picking_out_form

                mrp.product_product_normal_form_supply_view
                project_mrp.product_product_normal_form_supply_view
                sale_service.product_product_normal_form_supply_view
                purchase.product_product_normal_form_procurement_help_view
                purchase_requisition.product_normal_form_view_inherit
                stock_no_autopicking.view_product_form_auto_pick
            procurement.product_form_view_procurement_button
            point_of_sale.product_normal_form_view
            product_expiry.view_product_form_expiry
            project_mrp.view_product_task_form
            sale_service.view_product_task_form
        stock.view_normal_procurement_locations_form

        stock.view_normal_property_acc_form
        stock.view_category_property_form

    """.splitlines()))

    for v in views:
        util.remove_record(cr, v)
