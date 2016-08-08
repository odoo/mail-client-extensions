# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.delete_model(cr, 'report.point_of_sale.report_usersproduct')
