# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # If slow, see below for a way to bootstrap these fields using a specific upgrade script
    # https://github.com/odoo/migration-scripts/commit/f4caab2e581d87d03a6f3d0399686dc4a411ad2b#diff-fa65bc6a3467654469241afeb52fd3ee
    POL = util.env(cr)["purchase.order.line"].with_context(**{"raise-exception": False})
    query = "SELECT id FROM purchase_order_line WHERE qty_invoiced IS NULL"
    util.recompute_fields(cr, POL, ["qty_invoiced", "qty_received"], query=query)

    query = "SELECT id FROM purchase_order_line WHERE price_tax IS NULL"
    fields = ["price_tax", "price_subtotal", "price_total"]
    util.recompute_fields(cr, "purchase.order.line", fields, chunk_size=500, query=query)
