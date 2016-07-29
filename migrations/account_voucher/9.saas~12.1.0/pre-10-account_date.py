# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'account_voucher', 'account_date', 'date')
    cr.execute("UPDATE account_voucher SET account_date=date")
