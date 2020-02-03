# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util
import logging

_logger = logging.getLogger("odoo.addons.base.maintenance.migration.stock_account." + __name__)


def migrate(cr, version):
    pv = util.parse_version
    # Reintroduce remaining quantity
    util.create_column(cr, "stock_valuation_layer", "remaining_value", "numeric")

    if not util.column_exists(cr, "stock_move", "remaining_value") and pv(version) >= pv("saas~12.4"):
        _logger.warning("Cannot compute field `remaining_value`")
    else:
        cr.execute(
            """
            UPDATE stock_valuation_layer svl
               SET remaining_value = CASE
                      WHEN in_loc.usage != 'internal' THEN 0
                      WHEN out_loc.usage != 'internal' THEN sm.remaining_value
                   END
              FROM stock_move sm, stock_location in_loc, stock_location out_loc
             WHERE svl.stock_move_id = sm.id
               AND sm.location_id = in_loc.id
               AND sm.location_dest_id = out_loc.id
        """
        )

    util.remove_record(cr, "stock_account.stock_history_rule")
    util.remove_view(cr, "stock_account.view_stock_quantity_history")
    util.remove_view(cr, "stock_account.product_normal_form_view_inherit")
