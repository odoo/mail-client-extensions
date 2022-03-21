# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
            UPDATE account_move_line aml
               SET purchase_line_id = invl.purchase_line_id
              FROM invl_aml_mapping m
              JOIN account_invoice_line invl ON invl.id = m.invl_id
             WHERE m.aml_id = aml.id
            """,
            table="account_move_line",
            alias="aml",
        ),
    )
    util.remove_column(cr, "account_move_purchase_order_rel", "account_move_id")
    cr.execute("ALTER TABLE account_move_purchase_order_rel RENAME COLUMN account_invoice_id TO account_move_id")
