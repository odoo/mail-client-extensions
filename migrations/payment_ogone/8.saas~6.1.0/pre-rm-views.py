# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'payment_ogone.transaction_form_ogone')
