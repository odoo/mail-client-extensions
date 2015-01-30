# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'account_voucher.view_sale_receipt_report_graph',
                          'account_voucher.view_sale_receipt_report_pivot')
