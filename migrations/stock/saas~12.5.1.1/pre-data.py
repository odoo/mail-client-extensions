# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("{delivery,stock}.mail_template_data_delivery_confirmation"))

    util.force_noupdate(cr, "stock.sequence_stock_scrap", True)

    util.rename_xmlid(cr, *eb("stock.label_transfer_template_view{,_zpl}"))
    util.rename_xmlid(cr, "stock.label_transfer_template", "stock.action_label_transfer_template_zpl")

    util.remove_record(cr, "stock.product_pulled_flow_comp_rule")
    util.remove_menus(cr, [util.ref(cr, "stock.menu_variants_action"), util.ref(cr, "stock.menu_valuation")])

    util.remove_view(cr, "stock.view_move_picking_form")
    util.remove_record(cr, "stock.action_assign_a_responsible")
    util.remove_record(cr, "stock.action_picking_tree")
    util.remove_record(cr, "stock.action_picking_tree_done")
    util.remove_record(cr, "stock.action_picking_tree_done_grouped")
    # TODO force empty context on some actions

    util.remove_record(cr, "stock.quantsact")
    util.remove_view(cr, "stock.assets_tests")
    util.remove_record(cr, "stock.act_stock_warehouse_2_stock_warehouse_orderpoint")

    util.remove_view(cr, "stock.view_stock_picking_responsible_form")
    util.remove_record(cr, "stock.stock_assign_responsible_action")
    util.remove_record(cr, "stock.action_stock_quantity_history")
