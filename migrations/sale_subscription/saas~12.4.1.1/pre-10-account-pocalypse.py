# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'account_move_line', 'subscription_id', 'int4')
    util.create_column(cr, 'account_move_line', 'subscription_start_date', 'date')
    util.create_column(cr, 'account_move_line', 'subscription_end_date', 'date')
    util.create_column(cr, 'account_move_line', 'subscription_mrr', 'float')

    with util.disable_triggers(cr, "account_move_line"):
        cr.execute('''
            UPDATE account_move_line aml
               SET subscription_id = invl.subscription_id,
                   subscription_start_date = invl.subscription_start_date,
                   subscription_end_date = invl.subscription_end_date,
                   subscription_mrr = invl.subscription_mrr
              FROM account_invoice_line invl
              JOIN invl_aml_mapping mapping ON mapping.invl_id = invl.id
             WHERE mapping.is_invoice_line IS TRUE
               AND mapping.aml_id=aml.id
        ''')
