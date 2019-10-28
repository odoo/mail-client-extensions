# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "use_propagation_minimum_delta")

    # new inventories
    util.create_m2m(cr, 'stock_inventory_stock_location_rel', 'stock_inventory', 'stock_location')
    cr.execute("""
        INSERT INTO stock_inventory_stock_location_rel (stock_inventory_id,stock_location_id)
            SELECT id, location_id
              FROM stock_inventory WHERE state in ('draft', 'confirm')
    """)
    util.create_m2m(cr, 'product_product_stock_inventory_rel', 'stock_inventory', 'product_product')
    cr.execute("""
        INSERT INTO product_product_stock_inventory_rel (stock_inventory_id, product_product_id)
            SELECT id, product_id
              FROM stock_inventory
             WHERE state in ('draft', 'confirm')
               AND product_id IS NOT NULL
    """)

    # convert categ_id into product_ids
    cr.execute("""
        INSERT INTO product_product_stock_inventory_rel (stock_inventory_id, product_product_id)
            SELECT si.id, pp.id FROM product_product pp
            INNER JOIN product_template pt ON pt.id = pp.product_tmpl_id
            INNER JOIN product_category pc ON pc.id = pt.categ_id
            INNER JOIN stock_inventory si ON si.category_id = pc.id
            WHERE si.category_id is not null AND si.state='confirm'
    """)
    # convert lot_id into product_ids
    cr.execute("""
        INSERT INTO product_product_stock_inventory_rel (stock_inventory_id, product_product_id)
            SELECT si.id, pp.id FROM product_product pp
            INNER JOIN stock_production_lot spl ON spl.product_id = pp.id
            INNER JOIN stock_inventory si on si.lot_id = spl.id
            WHERE si.lot_id is not null AND si.state='confirm'
    """)
    # convert package_id into product_ids
    cr.execute("""
        INSERT INTO product_product_stock_inventory_rel (stock_inventory_id, product_product_id)
            SELECT si.id, pp.id FROM product_product pp
            INNER JOIN stock_quant sq ON sq.product_id = pp.id
            INNER JOIN stock_quant_package sqp ON sqp.id = sq.package_id
            INNER JOIN stock_inventory si on si.package_id = sqp.id
            WHERE si.package_id is not null AND si.state='confirm'
    """)

    util.remove_field(cr, "stock.inventory", "location_id")
    util.remove_field(cr, "stock.inventory", "product_id")
    util.remove_field(cr, "stock.inventory", "package_id")
    util.remove_field(cr, "stock.inventory", "partner_id")
    util.remove_field(cr, "stock.inventory", "lot_id")
    util.remove_field(cr, "stock.inventory", "category_id")
    util.remove_field(cr, "stock.inventory", "exhausted")

    util.create_column(cr, "stock_inventory", "start_empty", "boolean")

    util.create_column(cr, "stock_inventory_line", "is_editable", "boolean")
    util.create_column(cr, "stock_inventory_line", "inventory_date", "date")

    util.rename_field(cr, "stock.move", "propagate", "propagate_cancel")
    util.create_column(cr, "stock_move", "propagate_date", "boolean")
    util.create_column(cr, "stock_move", "propagate_date_minimum_delta", "int4")

    util.rename_field(cr, "stock.rule", "propagate", "propagate_cancel")
    util.create_column(cr, "stock_rule", "propagate_date", "boolean")
    util.create_column(cr, "stock_rule", "propagate_date_minimum_delta", "int4")
    cr.execute("UPDATE stock_rule SET propagate_date = true, propagate_date_minimum_delta = 1")

    # fill company_id with the warehouse one on stock_picking_type
    util.create_column(cr, "stock_picking_type", "company_id", "int4")
    util.remove_field(cr, "stock.picking.type", "show_reserved")
    cr.execute("""
        UPDATE stock_picking_type spt
           SET company_id = sw.company_id
          FROM stock_warehouse sw
         WHERE spt.warehouse_id = sw.id
    """)
    cr.execute(
        "SELECT 1 FROM res_groups_implied_rel WHERE gid=%s AND hid IN (%s)",
        [
            util.ref(cr, "base.group_user"),
            (
                util.ref(cr, "stock.group_production_lot"),
                util.ref(cr, "stock.group_stock_multi_locations"),
                util.ref(cr, "stock.group_tracking_lot"),
            ),
        ],
    )
    if cr.rowcount:
        cr.execute("UPDATE stock_picking_type SET show_operations=true")

    util.remove_record(cr, 'stock.action_inventory_line_tree')
    util.remove_view(cr, 'stock.view_stock_move_nosuggest_operations')
    util.remove_record(cr, 'stock.lot_open_quants')
    util.remove_record(cr, 'stock.product_open_quants')
    util.remove_view(cr, 'stock.view_production_lot_form_simple')

    util.remove_model(cr, 'stock.change.product.qty')
    util.remove_view(cr, 'stock.view_change_product_quantity')
