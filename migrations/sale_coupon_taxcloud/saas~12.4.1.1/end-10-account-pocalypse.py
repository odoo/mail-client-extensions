# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
            UPDATE account_move_line ml
               SET price_taxcloud = il.price_taxcloud
              FROM account_invoice_line il
              JOIN invl_aml_mapping m
                ON il.id = m.invl_id
             WHERE ml.id = m.aml_id
               AND ml.price_taxcloud != il.price_taxcloud
            """,
            "account_move_line",
            prefix="ml.",
        ),
    )
