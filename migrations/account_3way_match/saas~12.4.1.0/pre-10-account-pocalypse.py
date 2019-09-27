# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'account_move', 'release_to_pay', 'varchar')
    util.create_column(cr, 'account_move', 'release_to_pay_manual', 'varchar')
    util.create_column(cr, 'account_move', 'force_release_to_pay', 'boolean')
