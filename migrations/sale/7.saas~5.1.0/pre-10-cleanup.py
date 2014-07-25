# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # this view contains deleted fields (type, ...)
    util.remove_record(cr, 'sale.view_order_form')

