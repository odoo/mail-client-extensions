# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.parallel_execute(
        cr,
        util.explode_query_range(
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
            table="account_move_line",
            alias="aml",
        ),
    )
