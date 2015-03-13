# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.drop_depending_views(cr, 'hr_holidays', 'state')

    util.create_column(cr, 'hr_holidays', 'payslip_status', 'boolean')
    cr.execute("UPDATE hr_holidays SET payslip_status=true WHERE state='validate'")
