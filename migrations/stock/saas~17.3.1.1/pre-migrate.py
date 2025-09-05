from odoo import api, models
from odoo.tools.safe_eval import safe_eval

from odoo.upgrade import util


class PickingType(models.Model):
    _name = "stock.picking.type"
    _inherit = ["stock.picking.type"]
    _module = "stock"

    @api.constrains("default_location_dest_id")
    def _check_default_location(self):
        pass


class StockWarehouse(models.Model):
    _name = "stock.warehouse"
    _inherit = ["stock.warehouse"]
    _module = "stock"

    def _check_company(self, fnames=None):
        return super()._check_company(self.env.context.get("upgrade_check_company_write_vals", fnames))


def migrate(cr, version):
    util.remove_column(cr, "stock_move_line", "product_category_name")
    util.remove_column(cr, "stock_warehouse_orderpoint", "qty_to_order")
    util.remove_field(cr, "res.config.settings", "group_stock_storage_categories")
    util.remove_record(cr, "stock.group_stock_storage_categories")
    util.remove_record(cr, "stock.menu_reordering_rules_config")
    util.create_column(cr, "stock_putaway_rule", "sublocation", "varchar", default="no")

    # Putaway sublocation strategy will be set to 'closest location
    # for rules having storage category set
    query = """
        UPDATE stock_putaway_rule
           SET sublocation = 'closest_location'
         WHERE storage_category_id IS NOT NULL
    """
    cr.execute(query)

    util.create_column(cr, "product_template", "is_storable", "boolean")
    util.explode_execute(
        cr,
        """
        UPDATE product_template
           SET is_storable = TRUE
         WHERE type = 'product'
        """,
        table="product_template",
    )

    def adapter_move(leaf, _or, _neg):
        # Adapt the selection value 'product' in `stock.move.product_type` to use
        # `is_storable` boolean field instead, before removal of `product_type`
        left, op, right = leaf
        if op == "in" and isinstance(right, (tuple, list)) and set(right) == {"product", "consu"}:
            return [(1, "=", 1)]
        if right in ("product", "consu") or (isinstance(right, (tuple, list)) and len(right) == 1):
            path = left.split(".")
            path[-1] = "is_storable"
            new_left = ".".join(path)
            if "product" in right or right == "product":
                return [(new_left, "=", op in ("=", "in"))]
            elif "consu" in right or right == "consu":
                return [(new_left, "=", op not in ("=", "in"))]
        return [leaf]

    util.change_field_selection_values(cr, "product.template", "type", {"product": "consu"})

    util.adapt_domains(cr, "stock.move", "product_type", "product_type", adapter=adapter_move)
    util.remove_field(cr, "stock.move", "product_type")

    # Add default destination to either Customers or Warehouse/Stock
    customer_id = util.ref(cr, "stock.stock_location_customers")
    cr.execute(
        """
        WITH default_company_locs AS (
               SELECT sw.company_id,
                      (array_agg(sw.lot_stock_id ORDER BY sw.id))[1] AS lot_stock_id
                 FROM stock_warehouse sw
                WHERE sw.active = True
             GROUP BY sw.company_id
        ),
        customer_locs AS (
               SELECT sl.company_id,
                      (array_agg(sl.id ORDER BY sl.active DESC, sl.id))[1] AS id
                 FROM stock_location sl
                WHERE sl.usage = 'customer'
             GROUP BY sl.company_id
        )
        UPDATE stock_picking_type spt
           SET default_location_dest_id = CASE WHEN spt.code IN ('outgoing', 'dropship') THEN COALESCE(%s, ccl.id, ncl.id)
                                               ELSE COALESCE(sw.lot_stock_id, dcl.lot_stock_id)
                                           END
          FROM stock_picking_type spt2
     LEFT JOIN stock_warehouse sw
            ON spt2.warehouse_id = sw.id
          JOIN default_company_locs dcl
            ON spt2.company_id = dcl.company_id
     LEFT JOIN customer_locs ncl
            ON ncl.company_id IS NULL
     LEFT JOIN customer_locs ccl
            ON spt2.company_id = ccl.company_id
         WHERE spt.default_location_dest_id IS NULL
           AND spt.id = spt2.id
    """,
        [customer_id],
    )

    # Add default source to either Vendors or Warehouse/Stock
    vendor_id = util.ref(cr, "stock.stock_location_suppliers")
    cr.execute(
        """
        WITH default_company_locs AS (
               SELECT sw.company_id,
                      (array_agg(sw.lot_stock_id ORDER BY sw.id))[1] AS lot_stock_id
                 FROM stock_warehouse sw
                WHERE sw.active = True
             GROUP BY sw.company_id
        ),
        vendor_locs AS (
               SELECT sl.company_id,
                      (array_agg(sl.id ORDER BY sl.active DESC, sl.id))[1] AS id
                 FROM stock_location sl
                WHERE sl.usage = 'supplier'
             GROUP BY sl.company_id
        )
        UPDATE stock_picking_type spt
           SET default_location_src_id = CASE WHEN spt.code IN ('incoming', 'dropship') THEN COALESCE(%s, cvl.id, nvl.id)
                                              ELSE COALESCE(sw.lot_stock_id, dcl.lot_stock_id)
                                          END
          FROM stock_picking_type spt2
     LEFT JOIN stock_warehouse sw
            ON spt2.warehouse_id = sw.id
          JOIN default_company_locs dcl
            ON spt2.company_id = dcl.company_id
     LEFT JOIN vendor_locs nvl
            ON nvl.company_id IS NULL
     LEFT JOIN vendor_locs cvl
            ON spt2.company_id = cvl.company_id
         WHERE spt.default_location_src_id IS NULL
           AND spt.id = spt2.id
    """,
        [vendor_id],
    )
    actions = ["action_picking_tree_outgoing", "action_picking_tree_internal", "action_picking_tree_incoming"]
    fix_context(cr, "stock", actions, "default_company_id", "allowed_company_ids[0]")


def fix_context(cr, module, actions, key, value):
    cr.execute(
        """
        SELECT aw.id, aw.context
          FROM ir_model_data AS md
          JOIN ir_act_window AS aw
            ON md.model = 'ir.actions.act_window'
           AND md.res_id = aw.id
         WHERE md.module = %s
           AND md.name IN %s
           AND md.noupdate
        """,
        [module, tuple(actions)],
    )
    # Remove context key that is no longer valid
    for id, raw_context in cr.fetchall():
        context = safe_eval(raw_context, util.SelfPrintEvalContext(), nocopy=True)
        if str(context.pop(key, "")) == value:
            cr.execute("UPDATE ir_act_window SET context = %s WHERE id = %s", [str(context), id])
