# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    POL = util.env(cr)["purchase.order.line"].with_context(**{"raise-exception": False})
    cr.execute("SELECT id FROM purchase_order_line WHERE qty_invoiced IS NULL")
    ids = [r[0] for r in cr.fetchall()]
    util.recompute_fields(cr, POL, ["qty_invoiced", "qty_received"], ids=ids)

    cr.execute("SELECT id FROM purchase_order_line WHERE price_tax IS NULL")
    ids = [r[0] for r in cr.fetchall()]
    fields = ["price_tax", "price_subtotal", "price_total"]
    util.recompute_fields(cr, "purchase.order.line", fields, chunk_size=500, ids=ids)
