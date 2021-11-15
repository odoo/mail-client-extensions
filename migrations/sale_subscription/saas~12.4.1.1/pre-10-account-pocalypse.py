# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'account_move_line', 'subscription_id', 'int4')
    util.create_column(cr, 'account_move_line', 'subscription_start_date', 'date')
    util.create_column(cr, 'account_move_line', 'subscription_end_date', 'date')
    util.create_column(cr, 'account_move_line', 'subscription_mrr', 'numeric')
