# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'account_move_line', 'subscription_id', 'int4')
    util.create_column(cr, 'account_move_line', 'subscription_start_date', 'date')
    util.create_column(cr, 'account_move_line', 'subscription_end_date', 'date')
    util.create_column(cr, 'account_move_line', 'subscription_mrr', 'float')

    util.parallel_execute(
        cr,
        util.explode_query(
            cr,
            """
            UPDATE account_move_line aml
               SET subscription_id = invl.subscription_id,
                   subscription_start_date = invl.subscription_start_date,
                   subscription_end_date = invl.subscription_end_date,
                   subscription_mrr = invl.subscription_mrr
              FROM invl_aml_mapping m
              JOIN account_invoice_line invl ON invl.id = m.invl_id
             WHERE m.aml_id = aml.id
            """,
            prefix="aml.",
        ),
    )
