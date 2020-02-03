# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "stock_move_line", "is_landed_costs_line", "boolean")
    cr.execute(
        """
        UPDATE stock_move_line l
           SET is_landed_costs_line = t.landed_cost_ok
          FROM product_product p, product_template t
         WHERE p.id = l.product_id
           AND t.id = p.product_tmpl_id
    """
    )

    util.remove_field(cr, "product.template", "split_method")
    util.create_column(cr, "res_company", "lc_journal_id", "int4")
    util.create_column(cr, "stock_landed_cost", "vendor_bill_id", "int4")
    util.remove_field(cr, "stock.valuation.adjustment.lines", "former_cost_per_unit")

    util.remove_view(cr, "stock_landed_costs.view_stock_landed_cost_type_form")
    util.remove_view(cr, "stock_landed_costs.stock_landed_cost_tree_view")
    util.remove_record(cr, "stock_landed_costs.stock_landed_cost_type_action")
    util.remove_record(cr, "stock_landed_costs.stock_landed_cost_type_action1")
    util.remove_record(cr, "stock_landed_costs.stock_landed_cost_type_action2")
    util.remove_menus(cr, [util.ref(cr, "stock_landed_costs.menu_stock_landed_cost_type")])
