# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util
import logging

_logger = logging.getLogger("odoo.addons.base.maintenance.migration.stock_account." + __name__)


def migrate(cr, version):
    pv = util.parse_version
    # Reintroduce remaining quantity
    util.create_column(cr, "stock_valuation_layer", "remaining_value", "numeric")

    util.remove_record(cr, "stock_account.stock_history_rule")
    util.remove_view(cr, "stock_account.view_stock_quantity_history")
    util.remove_view(cr, "stock_account.product_normal_form_view_inherit")
