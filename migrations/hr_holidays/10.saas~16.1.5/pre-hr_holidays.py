# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    util.rename_field(cr, 'hr.holidays', 'manager_id', 'first_approver_id')
    util.rename_field(cr, 'hr.holidays', 'manager_id2', 'second_approver_id')
