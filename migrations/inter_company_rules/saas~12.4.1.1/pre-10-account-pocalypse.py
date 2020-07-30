# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'account_move', 'auto_generated', 'boolean')
    util.create_column(cr, 'account_move', 'auto_invoice_id', 'int4')
