# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # only recompute for order with a currency != company currency, otherwise 1.0
    cr.execute("""
        UPDATE pos_order
        SET currency_rate = 1
        FROM product_pricelist p,res_company c
        WHERE pos_order.company_id=c.id
          AND pos_order.pricelist_id=p.id
          AND p.currency_id = c.currency_id
    """)
    cr.execute("""
        SELECT id FROM pos_order WHERE currency_rate IS NULL
    """)
    recompute_ids = [o[0] for o in cr.fetchall()]
    util.recompute_fields(cr, "pos.order", ["currency_rate"], ids=recompute_ids)
