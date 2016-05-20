# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'base.menu_procurement_management_supplier_name',
                      'purchase.menu_procurement_management_supplier_name')
