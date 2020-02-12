# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "product_template", "split_method_landed_cost", "varchar")
    util.create_column(cr, "stock_landed_cost", "target_model", "varchar")

    # target_model is required
    cr.execute("UPDATE stock_landed_cost SET target_model='picking' WHERE target_model IS NULL")
