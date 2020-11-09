# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # new field `ordered_qty` added on stock.move and stock.pack.operation
    # They aimed to store the initially ordered quantity in case the move/operation qty change
    # This can be invalid but we will initiate these columns with the currently processed qty

    util.create_column(cr, "stock_move", "ordered_qty", "numeric")
    query = "UPDATE stock_move SET ordered_qty = product_uom_qty"
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="stock_move"))

    util.create_column(cr, "stock_pack_operation", "ordered_qty", "numeric")
    query = "UPDATE stock_pack_operation SET ordered_qty = product_qty"
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="stock_pack_operation"))

    # beside the logic would say when should go from `auto` (Automatic)
    # to `transparent` (Automatic No Step Added), the code in `_apply` function only treat
    # `transparent` as a special case (https://git.io/voUPo). `auto` and `manual` are actually
    # behaving the same way...
    cr.execute("UPDATE stock_location_path SET auto='manual' WHERE auto='auto'")

    util.rename_field(cr, "stock.pack.operation", "processed_boolean", "is_done")

    # related fields without type set -> default to float, which worked.
    cr.execute("ALTER TABLE procurement_rule ALTER COLUMN route_sequence TYPE integer")
    cr.execute("ALTER TABLE stock_location_path ALTER COLUMN route_sequence TYPE integer")
