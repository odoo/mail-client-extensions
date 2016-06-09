# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'sale_contract.close_reason_4', 'sale_contract.close_reason_5')
    util.rename_xmlid(cr, 'sale_contract.close_reason_3', 'sale_contract.close_reason_4')
