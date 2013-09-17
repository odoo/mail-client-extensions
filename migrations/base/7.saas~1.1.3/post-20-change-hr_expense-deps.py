# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # in march 2013, hr_expense got a new depend: account_accountant
    util.new_module_dep(cr, 'hr_expense', 'account_accountant')
