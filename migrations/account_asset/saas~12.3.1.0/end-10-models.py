# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, 'account.asset', 'category_id')
    util.remove_field(cr, 'account.invoice.line', 'asset_start_date')
    util.remove_field(cr, 'account.invoice.line', 'asset_end_date')
